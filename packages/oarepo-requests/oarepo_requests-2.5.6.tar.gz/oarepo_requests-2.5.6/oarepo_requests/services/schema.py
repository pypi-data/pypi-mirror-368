#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Enhancements to the request schema."""

from __future__ import annotations

from typing import Any

import marshmallow as ma
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.links import Link, LinksTemplate
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.records import is_published_record


def get_links_schema() -> ma.fields.Dict:
    """Get links schema."""
    return ma.fields.Dict(
        keys=ma.fields.String()
    )  # value is either string or dict of strings (for actions)


class RequestTypeSchema(ma.Schema):
    """Request type schema."""

    type_id = ma.fields.String()
    """Type ID of the request type."""

    links = get_links_schema()
    """Links to the request type."""

    @ma.post_dump
    def _create_link(self, data: dict, **kwargs: Any) -> dict:
        if "links" in data:
            return data
        if "record" not in self.context:
            raise ma.ValidationError(
                "record not in context for request types serialization"
            )
        type_id = data["type_id"]
        # current_request_type_registry.lookup(type_id, quiet=True)
        record = self.context["record"]
        service = get_record_service_for_record(record)
        link = ConditionalLink(
            cond=is_published_record,
            if_=Link(f"{{+api}}{service.config.url_prefix}{{id}}/requests/{type_id}"),
            else_=Link(
                f"{{+api}}{service.config.url_prefix}{{id}}/draft/requests/{type_id}"
            ),
        )
        template = LinksTemplate({"create": link}, context={"id": record["id"]})
        data["links"] = {"actions": template.expand(self.context["identity"], record)}
        return data


class NoReceiverAllowedGenericRequestSchema(GenericRequestSchema):
    """A mixin that allows serialization of requests without a receiver."""

    receiver = fields.Dict(allow_none=True)


class RequestsSchemaMixin:
    """A mixin that allows serialization of requests together with their request type."""

    requests = ma.fields.List(ma.fields.Nested(NoReceiverAllowedGenericRequestSchema))
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
