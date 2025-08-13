#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""API resource for applicable request types for a draft record."""

from __future__ import annotations

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import request_view_args

from oarepo_requests.resources.record.types.resource import RecordRequestTypesResource


class DraftRequestTypesResource(RecordRequestTypesResource):
    """API resource for applicable request types for a draft record."""

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""
        old_rules = super().create_url_rules()
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route(
                "GET",
                routes["list-applicable-requests-draft"],
                self.get_applicable_request_types_for_draft,
            )
        ]
        return url_rules + old_rules

    @request_view_args
    @response_handler(many=True)
    def get_applicable_request_types_for_draft(self) -> tuple[dict, int]:
        """List request types."""
        # TODO: split the resource to service-agnostic part (just the configuration)
        # and service-dependent part (the actual service)
        # this will then allow removing the type: ignore below
        hits = self.service.get_applicable_request_types_for_draft_record(  # type: ignore
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
        )
        return hits.to_dict(), 200
