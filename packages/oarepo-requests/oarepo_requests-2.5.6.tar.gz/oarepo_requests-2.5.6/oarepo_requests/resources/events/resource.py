#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Resource for request events/comments that lives on the extended url."""

from __future__ import annotations

from flask import g
from flask_resources import (
    from_conf,
    request_body_parser,
    request_parser,
    resource_requestctx,
    response_handler,
    route,
)
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import request_extra_args
from invenio_requests.proxies import current_event_type_registry
from invenio_requests.resources.events.resource import RequestCommentsResource


class OARepoRequestsCommentsResource(RequestCommentsResource, ErrorHandlersMixin):
    """OARepo extensions to invenio requests comments resource."""

    item_view_args_parser = request_parser(
        from_conf("request_item_view_args"), location="view_args"
    )

    data_parser = request_body_parser(
        parsers=from_conf("request_body_parsers"),
        default_content_type=from_conf("default_content_type"),
    )

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        base_routes = super().create_url_rules()
        routes = self.config.routes

        url_rules = [
            route("POST", routes["list-extended"], self.create_extended),
            route("POST", routes["event-type"], self.create_event),
            route(
                "POST",
                routes["event-type-extended"],
                self.create_event,
                endpoint="create_event_extended",
            ),
            route("GET", routes["item-extended"], self.read_extended),
            route("PUT", routes["item-extended"], self.update_extended),
            route("DELETE", routes["item-extended"], self.delete_extended),
            route("GET", routes["timeline-extended"], self.search_extended),
        ]
        return url_rules + base_routes

    # from parent
    def create_extended(self) -> tuple[dict, int]:
        """Create a new comment."""
        return super().create()

    def read_extended(self) -> tuple[dict, int]:
        """Read a comment."""
        return super().read()

    def update_extended(self) -> tuple[dict, int]:
        """Update a comment."""
        return super().update()

    def delete_extended(self) -> tuple[dict, int]:
        """Delete a comment."""
        return super().delete()

    def search_extended(self) -> tuple[dict, int]:
        """Search for comments."""
        return super().search()

    # list args parser in invenio parses request_id input through UUID instead of Str; does this have any relevance for us?
    @item_view_args_parser
    @request_extra_args
    @data_parser
    @response_handler()
    def create_event(self):
        """Create a comment."""
        type_ = current_event_type_registry.lookup(
            resource_requestctx.view_args["event_type"], quiet=True
        )
        item = self.service.create(
            identity=g.identity,
            request_id=resource_requestctx.view_args["request_id"],
            data=resource_requestctx.data,
            event_type=type_,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 201
