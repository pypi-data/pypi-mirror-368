#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""UI schemas for requests."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, cast

import marshmallow as ma
from invenio_pidstore.errors import (
    PersistentIdentifierError,
    PIDDeletedError,
)
from invenio_rdm_records.services.errors import RecordDeletedException
from invenio_requests.proxies import current_request_type_registry, current_requests
from invenio_requests.records import Request
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_requests.services.schemas import (
    CommentEventType,
    EventTypeMarshmallowField,
)
from marshmallow import validate
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_runtime.services.schema.marshmallow import BaseRecordSchema
from oarepo_runtime.services.schema.ui import LocalizedDateTime
from sqlalchemy.orm.exc import NoResultFound

from oarepo_requests.resolvers.ui import resolve
from oarepo_requests.services.schema import (
    NoReceiverAllowedGenericRequestSchema,
    RequestTypeSchema,
    get_links_schema,
)

if TYPE_CHECKING:
    from invenio_requests.customizations.request_types import RequestType
    from invenio_requests.records.api import RequestEvent


class UIReferenceSchema(ma.Schema):
    """UI schema for references."""

    reference = ma.fields.Dict(validate=validate.Length(equal=1))
    """Reference to the entity."""

    type = ma.fields.String()
    """Type of the entity."""

    label = ma.fields.String()
    """Label of the entity."""

    links = get_links_schema()
    """Links to the entity."""

    @ma.pre_dump
    def _create_reference(self, data: Any, **kwargs: Any) -> dict | None:
        if data:
            return dict(reference=data)
        return None

    @ma.post_dump
    def _dereference(self, data: dict, **kwargs: Any) -> dict[str, Any]:
        if "resolved" not in self.context:
            try:
                return cast(
                    "dict", resolve(self.context["identity"], data["reference"])
                )
            except PIDDeletedError:
                return {**data, "status": "removed"}
            except PersistentIdentifierError:
                return {**data, "status": "invalid"}
            except RecordDeletedException:
                return {**data, "status": "removed"}
        resolved_cache = self.context["resolved"]
        try:
            return resolved_cache.dereference(data["reference"])
        except PersistentIdentifierError:
            return {**data, "status": "invalid"}
        except RecordDeletedException:
            return {**data, "status": "deleted"}


class UIRequestSchemaMixin:
    """Mixin for UI request schemas."""

    created = LocalizedDateTime(dump_only=True)
    """Creation date of the request."""

    updated = LocalizedDateTime(dump_only=True)
    """Update date of the request."""

    name = ma.fields.String()
    """Name of the request."""

    description = ma.fields.String()
    """Description of the request."""

    stateful_name = ma.fields.String(dump_only=True)
    """Stateful name of the request, as given by the request type."""

    stateful_description = ma.fields.String(dump_only=True)
    """Stateful description of the request, as given by the request type."""

    created_by = ma.fields.Nested(UIReferenceSchema)
    """Creator of the request."""

    receiver = ma.fields.Nested(UIReferenceSchema)
    """Receiver of the request."""

    topic = ma.fields.Nested(UIReferenceSchema)
    """Topic of the request."""

    links = get_links_schema()
    """Links to the request."""

    payload = ma.fields.Raw()
    """Extra payload of the request."""

    status_code = ma.fields.String()
    """Status code of the request."""

    @ma.pre_dump
    def _convert_dates_for_localized(self, data: dict, **kwargs: Any) -> dict:
        if isinstance(data.get("created"), str):
            data["created"] = datetime.datetime.fromisoformat(data["created"])

        if isinstance(data.get("updated"), str):
            data["updated"] = datetime.datetime.fromisoformat(data["updated"])

        if isinstance(data.get("expires_at"), str):
            data["expires_at"] = datetime.datetime.fromisoformat(data["expires_at"])

        return data

    @ma.pre_dump
    def _add_type_details(self, data: dict, **kwargs: Any) -> dict:
        """Add details taken from the request type to the serialized request."""
        if isinstance(data.get("created"), str):
            data["created"] = datetime.datetime.fromisoformat(data["created"])
        if isinstance(data.get("updated"), str):
            data["updated"] = datetime.datetime.fromisoformat(data["updated"])
        type = data["type"]
        type_obj = current_request_type_registry.lookup(type, quiet=True)
        if hasattr(type_obj, "description"):
            data["description"] = type_obj.description
        if hasattr(type_obj, "name"):
            data["name"] = type_obj.name

        stateful_name, stateful_description = self._get_stateful_labels(type_obj, data)
        data["stateful_name"] = stateful_name or data["name"]
        data["stateful_description"] = stateful_description or data["description"]

        return data

    def _get_stateful_labels(
        self, type_obj: RequestType, data: dict
    ) -> tuple[str | None, str | None]:
        stateful_name = None
        stateful_description = None
        try:
            topic_dict = data.get("topic")
            if not topic_dict:
                return stateful_name, stateful_description

            topic = ResolverRegistry.resolve_entity(topic_dict, False)
            if topic:
                request_obj = None
                if hasattr(type_obj, "stateful_name"):
                    request_obj = Request.get_record(data["id"])
                    stateful_name = type_obj.stateful_name(
                        identity=self.context["identity"],  # type: ignore
                        topic=topic,
                        request=request_obj,
                    )
                if hasattr(type_obj, "stateful_description"):
                    if request_obj is None:
                        request_obj = Request.get_record(data["id"])
                    stateful_description = type_obj.stateful_description(
                        identity=self.context["identity"],  # type: ignore
                        topic=topic,
                        request=request_obj,
                    )
        except (PersistentIdentifierError, NoResultFound, ValueError):
            pass

        return stateful_name, stateful_description

    @ma.pre_dump
    def _process_status(self, data: dict, **kwargs: Any) -> dict:
        data["status_code"] = data["status"]
        data["status"] = _(data["status"].capitalize())
        return data


class UIBaseRequestSchema(UIRequestSchemaMixin, NoReceiverAllowedGenericRequestSchema):
    """Base schema for oarepo requests."""


class UIRequestTypeSchema(RequestTypeSchema):
    """UI schema for request types."""

    name = ma.fields.String()
    """Name of the request type."""

    description = ma.fields.String()
    """Description of the request type."""

    fast_approve = ma.fields.Boolean()
    """Whether the request type can be fast approved."""

    stateful_name = ma.fields.String(dump_only=True)
    """Stateful name of the request type."""

    stateful_description = ma.fields.String(dump_only=True)
    """Stateful description of the request type."""

    dangerous = ma.fields.Boolean(dump_only=True)
    """Whether the request type is dangerous (for example, delete stuff)."""

    editable = ma.fields.Boolean(dump_only=True)
    """Whether the request type is editable.
    
    Editable requests are not automatically submitted, they are kept in open state
    until the user decides to submit them."""

    has_form = ma.fields.Boolean(dump_only=True)
    """Whether the request type has a form."""

    @ma.post_dump
    def _add_type_details(self, data: dict, **kwargs: Any) -> dict:
        """Serialize details from request type."""
        type = data["type_id"]
        type_obj = current_request_type_registry.lookup(type, quiet=True)
        if hasattr(type_obj, "description"):
            data["description"] = type_obj.description
        if hasattr(type_obj, "name"):
            data["name"] = type_obj.name
        if hasattr(type_obj, "dangerous"):
            data["dangerous"] = type_obj.dangerous
        if hasattr(type_obj, "is_editable"):
            data["editable"] = type_obj.is_editable
        if hasattr(type_obj, "has_form"):
            data["has_form"] = type_obj.has_form

        if hasattr(type_obj, "stateful_name"):
            data["stateful_name"] = type_obj.stateful_name(
                identity=self.context["identity"], topic=self.context["topic"]
            )
        if hasattr(type_obj, "stateful_description"):
            data["stateful_description"] = type_obj.stateful_description(
                identity=self.context["identity"], topic=self.context["topic"]
            )
        return data


class UIRequestsSerializationMixin(ma.Schema):
    """Mixin for serialization of record that adds information from request type."""

    @ma.post_dump(pass_original=True)
    def _add_request_types(
        self, data: dict, original_data: dict, **kwargs: Any
    ) -> dict:
        """If the expansion is requested, add UI form of request types and requests to the serialized record."""
        expanded = data.get("expanded", {})
        if not expanded:
            return data
        context = {**self.context, "topic": original_data}
        if "request_types" in expanded:
            expanded["request_types"] = UIRequestTypeSchema(context=context).dump(
                expanded["request_types"], many=True
            )
        if "requests" in expanded:
            expanded["requests"] = UIBaseRequestSchema(context=context).dump(
                expanded["requests"], many=True
            )
        return data


class UIBaseRequestEventSchema(BaseRecordSchema):
    """Base schema for request events."""

    created = LocalizedDateTime(dump_only=True)
    """Creation date of the event."""

    updated = LocalizedDateTime(dump_only=True)
    """Update date of the event."""

    type = EventTypeMarshmallowField(dump_only=True)
    """Type of the event."""

    created_by = ma.fields.Nested(UIReferenceSchema)
    """Creator of the event."""

    permissions = ma.fields.Method("get_permissions", dump_only=True)
    """Permissions to act on the event."""

    payload = ma.fields.Raw()
    """Payload of the event."""

    def get_permissions(self, obj: RequestEvent) -> dict:
        """Return permissions to act on comments or empty dict."""
        type = self.get_attribute(obj, "type", None)
        is_comment = type == CommentEventType
        if is_comment:
            service = current_requests.request_events_service
            return {
                "can_update_comment": service.check_permission(
                    self.context["identity"], "update_comment", event=obj
                ),
                "can_delete_comment": service.check_permission(
                    self.context["identity"], "delete_comment", event=obj
                ),
            }
        else:
            return {}
