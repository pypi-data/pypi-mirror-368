#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base request type for OARepo requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.customizations import RequestType
from invenio_requests.customizations.states import RequestState
from invenio_requests.proxies import current_requests_service

from oarepo_requests.errors import OpenRequestAlreadyExists
from oarepo_requests.utils import classproperty, open_request_exists

from ..actions.generic import (
    OARepoAcceptAction,
    OARepoCancelAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from ..utils import (
    has_rights_to_accept_request,
    has_rights_to_submit_request,
    is_auto_approved,
    request_identity_matches,
)
from .ref_types import ModelRefTypes, ReceiverRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request

    from oarepo_requests.typing import EntityReference


class OARepoRequestType(RequestType):
    """Base request type for OARepo requests."""

    description = None

    dangerous = False

    def on_topic_delete(self, request: Request, topic: Record) -> None:
        """Cancel the request when the topic is deleted.

        :param request:         the request
        :param topic:           the topic
        """
        current_requests_service.execute_action(system_identity, request.id, "cancel")

    @classproperty[dict[str, RequestState]]
    def available_statuses(cls) -> dict[str, RequestState]:
        """Return available statuses for the request type.

        The status (open, closed, undefined) are used for request filtering.
        """
        return {**super().available_statuses, "created": RequestState.OPEN}

    @classproperty[bool]
    def has_form(cls) -> bool:
        """Return whether the request type has a form."""
        return hasattr(cls, "form")

    editable: bool | None = None
    """Whether the request type can be edited multiple times before it is submitted."""

    @classproperty[bool]
    def is_editable(cls) -> bool:
        """Return whether the request type is editable."""
        if cls.editable is not None:
            return cls.editable
        return cls.has_form  # noqa

    @classmethod
    def _create_marshmallow_schema(cls):
        """Create a marshmallow schema for this request type with required payload field."""
        schema = super()._create_marshmallow_schema()
        if (
            cls.payload_schema is not None
            and hasattr(schema, "fields")
            and "payload" in schema.fields
        ):
            schema.fields["payload"].required = True

        return schema

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: EntityReference,
        topic: Record,
        creator: EntityReference,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created.

        :param identity:        identity of the caller
        :param data:            data of the request
        :param receiver:        receiver of the request
        :param topic:           topic of the request
        :param creator:         creator of the request
        :param args:            additional arguments
        :param kwargs:          additional keyword arguments
        """
        current_requests_service.require_permission(
            identity, "create", record=topic, request_type=self, **kwargs
        )

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic.

        Used for checking whether there is any situation where the client can create
        a request of this type it's different to just using can create with no receiver
        and data because that checks specifically for situation without them while this
        method is used to check whether there is a possible situation a user might create
        this request eg. for the purpose of serializing a link on associated record
        """
        try:
            current_requests_service.require_permission(
                identity, "create", record=topic, request_type=cls, **kwargs
            )
        except PermissionDeniedError:
            return False
        return True

    allowed_topic_ref_types = ModelRefTypes()
    allowed_receiver_ref_types = ReceiverRefTypes()

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": OARepoSubmitAction,
            "accept": OARepoAcceptAction,
            "decline": OARepoDeclineAction,
            "cancel": OARepoCancelAction,
        }

    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the name of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.name

    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the description of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.description

    def string_by_state(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        # strings
        create: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        create_autoapproved: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submit: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_receiver: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_creator: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_others: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        accepted: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        declined: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        cancelled: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        created: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
    ) -> str | LazyString:
        """Return a string that varies by the state of the request.

        :param create:        string to be used on request type if user can create a request
        :param create_autoapproved: string to be used on request type if user can create a request
                                    and the request is auto approved
        :param submit:        string to be used on request type if user can submit a request
        :param accept_decline: string to be used on request type if user can accept or decline a request
        :param view:          string to be used on request type if user can view a request
        """

        def get_string(
            string: str | LazyString,
            identity: Identity,
            topic: Record,
            request: Request | None = None,
        ) -> str | LazyString:
            if callable(string):
                return string(identity, topic, request)
            return string

        if request:
            match request.status:
                case "submitted":
                    if has_rights_to_accept_request(request, identity):
                        return get_string(submitted_receiver, identity, topic, request)
                    if request_identity_matches(request.created_by, identity):
                        return get_string(submitted_creator, identity, topic, request)
                    return get_string(submitted_others, identity, topic, request)
                case "accepted":
                    return get_string(accepted, identity, topic, request)
                case "declined":
                    return get_string(declined, identity, topic, request)
                case "cancelled":
                    return get_string(cancelled, identity, topic, request)
                case "created":
                    if has_rights_to_submit_request(request, identity):
                        return get_string(submit, identity, topic, request)
                    return get_string(created, identity, topic, request)
                case _:
                    return (
                        f'Unknown label for status "{request.status}" in "{__file__}"'
                    )

        if is_auto_approved(self, identity=identity, topic=topic):
            return get_string(create_autoapproved, identity, topic, request)
        return get_string(create, identity, topic, request)


class NonDuplicableOARepoRequestType(OARepoRequestType):
    """Base request type for OARepo requests that cannot be duplicated.

    This means that on a single topic there can be only one open request of this type.
    """

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: EntityReference,
        topic: Record,
        creator: EntityReference,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created.

        :param identity:        identity of the caller
        :param data:            data of the request
        :param receiver:        receiver of the request
        :param topic:           topic of the request
        :param creator:         creator of the request
        :param args:            additional arguments
        :param kwargs:          additional keyword arguments
        """
        if open_request_exists(topic, self.type_id):
            raise OpenRequestAlreadyExists(self, topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if open_request_exists(topic, cls.type_id):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)
