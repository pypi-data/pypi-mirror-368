#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Draft record requests resource."""

from __future__ import annotations

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference

from oarepo_requests.resources.record.resource import RecordRequestsResource
from oarepo_requests.utils import stringify_first_val


class DraftRecordRequestsResource(RecordRequestsResource):
    """Draft record requests resource."""

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""
        old_rules = super().create_url_rules()
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route("GET", routes["list-requests-draft"], self.search_requests_for_draft),
            route("POST", routes["request-type-draft"], self.create_for_draft),
        ]
        return url_rules + old_rules

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_requests_for_draft(self) -> tuple[dict, int]:
        """Perform a search over the items."""
        hits = self.service.search_requests_for_draft(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

    @request_extra_args
    @request_view_args
    @request_data
    @response_handler()
    def create_for_draft(self) -> tuple[dict, int]:
        """Create an item."""
        items = self.service.create_for_draft(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.view_args["request_type"],
            topic_id=resource_requestctx.view_args[
                "pid_value"
            ],  # do in service; put type_id into service config, what about draft/not draft, different url?
            expand=(
                stringify_first_val(
                    resource_requestctx.data.pop("expand", False)
                )  # for what is this used, or can i just delete it
                if resource_requestctx.data
                else None
            ),
        )

        return items.to_dict(), 201
