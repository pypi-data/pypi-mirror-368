#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Patches to invenio service to allow for more flexible requests handling."""

from __future__ import annotations

from functools import cached_property, partial
from typing import TYPE_CHECKING, Any, Callable

from flask import current_app
from flask_babel import LazyString, force_locale
from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.records.params import FilterParam
from invenio_records_resources.services.records.params.base import ParamInterpreter
from invenio_requests.resources.events.config import RequestCommentsResourceConfig
from invenio_requests.resources.requests.config import (
    RequestSearchRequestArgsSchema,
    RequestsResourceConfig,
)
from invenio_requests.services.requests.config import (
    RequestSearchOptions,
    RequestsServiceConfig,
)
from invenio_requests.services.requests.params import IsOpenParam
from invenio_search.engine import dsl
from marshmallow import fields
from opensearch_dsl.query import Bool
from invenio_requests.notifications.generators import RequestParticipantsRecipient
from oarepo_requests.notifications.generators import OARepoRequestParticipantsRecipient
from oarepo_requests.resources.ui import (
    OARepoRequestEventsUIJSONSerializer,
    OARepoRequestsUIJSONSerializer,
)
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig

if TYPE_CHECKING:
    from flask.blueprints import BlueprintSetupState
    from flask_principal import Identity
    from flask_resources.serializers.base import BaseSerializer
    from opensearch_dsl.query import Query


class RequestOwnerFilterParam(FilterParam):
    """Filter requests by owner."""

    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
        """Apply the filter to the search."""
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter("term", **{self.field_name: identity.id})
        return search


class RequestAllAvailableFilterParam(ParamInterpreter):
    """A no-op filter that returns all requests that are readable by the current user."""

    def __init__(self, param_name, config):
        """Initialize the filter."""
        self.param_name = param_name
        super().__init__(config)

    @classmethod
    def factory(cls, param=None):
        """Create a new filter parameter."""
        return partial(cls, param)

    def apply(self, identity, search, params):
        """Apply the filter to the search - does nothing."""
        params.pop(self.param_name, None)
        return search


class RequestNotOwnerFilterParam(FilterParam):
    """Filter requests that are not owned by the current user.

    Note: invenio still does check that the user has the right to see the request,
    so this is just a filter to narrow down the search to requests, that the user
    can approve.
    """

    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
        """Apply the filter to the search."""
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter(
                Bool(must_not=[dsl.Q("term", **{self.field_name: identity.id})])
            )
        return search


class IsClosedParam(IsOpenParam):
    """Get just the closed requests."""

    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
        """Evaluate the is_closed parameter on the search."""
        if params.get("is_closed") is True:
            search = search.filter("term", **{self.field_name: True})
        elif params.get("is_closed") is False:
            search = search.filter("term", **{self.field_name: False})
        return search


class EnhancedRequestSearchOptions(RequestSearchOptions):
    """Searched options enhanced with additional filters."""

    params_interpreters_cls = RequestSearchOptions.params_interpreters_cls + [
        RequestOwnerFilterParam.factory("mine", "created_by.user"),
        RequestNotOwnerFilterParam.factory("assigned", "created_by.user"),
        RequestAllAvailableFilterParam.factory("all"),
        IsClosedParam.factory("is_closed"),
    ]


class ExtendedRequestSearchRequestArgsSchema(RequestSearchRequestArgsSchema):
    """Marshmallow schema for the extra filters."""

    mine = fields.Boolean()
    assigned = fields.Boolean()
    all = fields.Boolean()
    is_closed = fields.Boolean()


def override_invenio_requests_config(
    state: BlueprintSetupState, *args: Any, **kwargs: Any
) -> None:
    """Override the invenio requests configuration.

    This function is called from the blueprint setup function as this should be a safe moment
    to monkey patch the invenio requests configuration.
    """
    with state.app.app_context():
        # this monkey patch should be done better (support from invenio)
        RequestsServiceConfig.search = EnhancedRequestSearchOptions
        RequestsResourceConfig.request_search_args = (
            ExtendedRequestSearchRequestArgsSchema
        )
        # add extra links to the requests
        for k, v in OARepoRequestsServiceConfig.links_item.items():
            if k not in RequestsServiceConfig.links_item:
                RequestsServiceConfig.links_item[k] = v

        class LazySerializer:
            def __init__(self, serializer_cls: type[BaseSerializer]) -> None:
                self.serializer_cls = serializer_cls

            @cached_property
            def __instance(self) -> BaseSerializer:
                return self.serializer_cls()

            @property
            def serialize_object_list(self) -> Callable:
                return self.__instance.serialize_object_list

            @property
            def serialize_object(self) -> Callable:
                return self.__instance.serialize_object

        RequestsResourceConfig.response_handlers = {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                LazySerializer(OARepoRequestsUIJSONSerializer), headers=etag_headers
            ),
        }

        RequestCommentsResourceConfig.response_handlers = {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                LazySerializer(OARepoRequestEventsUIJSONSerializer),
                headers=etag_headers,
            ),
            **RequestCommentsResourceConfig.response_handlers,
        }

        from invenio_requests.proxies import current_request_type_registry
        from invenio_requests.services.requests.facets import status, type
        from oarepo_runtime.i18n import lazy_gettext as _

        status._value_labels = {
            "submitted": _("Submitted"),
            "expired": _("Expired"),
            "accepted": _("Accepted"),
            "declined": _("Declined"),
            "cancelled": _("Cancelled"),
            "created": _("Created"),
        }
        status._label = _("Request status")

        # add extra request types dynamically
        type._value_labels = {
            rt.type_id: rt.name for rt in iter(current_request_type_registry)
        }
        type._label = _("Type")


def override_invenio_notifications(
    state: BlueprintSetupState, *args: Any, **kwargs: Any
) -> None:
    with state.app.app_context():
        from invenio_notifications.services.generators import EntityResolve
        from invenio_requests.notifications.builders import (
            CommentRequestEventCreateNotificationBuilder,
        )

        from oarepo_requests.notifications.generators import RequestEntityResolve

        for r in CommentRequestEventCreateNotificationBuilder.context:
            if isinstance(r, EntityResolve) and r.key == "request.topic":
                break
        else:
            CommentRequestEventCreateNotificationBuilder.context.append(
                EntityResolve(key="request.topic"),
            )


        for r in CommentRequestEventCreateNotificationBuilder.recipients:
            if isinstance(r, RequestParticipantsRecipient):
                CommentRequestEventCreateNotificationBuilder.recipients.remove(r)
                CommentRequestEventCreateNotificationBuilder.recipients.append(OARepoRequestParticipantsRecipient(key="request"))
                break

        for idx, r in list(
            enumerate(CommentRequestEventCreateNotificationBuilder.context)
        ):
            if isinstance(r, EntityResolve) and r.key == "request":
                CommentRequestEventCreateNotificationBuilder.context[idx] = (
                    # entity resolver that adds the correct title if it is missing
                    RequestEntityResolve(
                        key="request",
                    )
                )

        from invenio_notifications.tasks import (
            dispatch_notification,
        )

        original_delay = dispatch_notification.delay

        def i18n_enabled_notification_delay(backend, recipient, notification):
            """Delay can not handle lazy strings, so we need to resolve them before calling the delay."""
            locale = None
            if isinstance(recipient, dict):
                locale = recipient.get("data", {}).get("preferences", {}).get("locale")
            locale = locale or current_app.config.get("BABEL_DEFAULT_LOCALE", "en")
            with force_locale(locale):
                notification = resolve_lazy_strings(notification)
            return original_delay(backend, recipient, notification)

        dispatch_notification.delay = i18n_enabled_notification_delay


def resolve_lazy_strings(data):
    if isinstance(data, dict):
        return {key: resolve_lazy_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [resolve_lazy_strings(item) for item in data]
    elif isinstance(data, LazyString):
        return str(data)
    else:
        return data
