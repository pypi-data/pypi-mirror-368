#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo extensions to invenio requests resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_headers,
    request_view_args,
)
from invenio_requests.proxies import current_requests_service
from invenio_requests.resources import RequestsResource

from oarepo_requests.utils import resolve_reference_dict, stringify_first_val

if TYPE_CHECKING:
    from invenio_requests.services.requests import RequestsService

    from ...services.oarepo.service import OARepoRequestsService
    from .config import OARepoRequestsResourceConfig


class OARepoRequestsResource(RequestsResource, ErrorHandlersMixin):
    """OARepo extensions to invenio requests resource."""

    def __init__(
        self,
        config: OARepoRequestsResourceConfig,
        oarepo_requests_service: OARepoRequestsService,
        invenio_requests_service: RequestsService = current_requests_service,
    ) -> None:
        """Initialize the service."""
        # so super methods can be used with original service
        super().__init__(config, invenio_requests_service)
        self.oarepo_requests_service = oarepo_requests_service

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes

        url_rules = [
            route("POST", p(routes["list"]), self.create),
            route(
                "POST",
                p(routes["list-extended"]),
                self.create,
                endpoint="extended_create",
            ),
            route("GET", p(routes["item-extended"]), self.read_extended),
            route("PUT", p(routes["item-extended"]), self.update),
        ]
        return url_rules

    @request_extra_args
    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def update(self) -> tuple[dict, int]:
        """Update a request with a new payload."""
        item = self.oarepo_requests_service.update(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            data=resource_requestctx.data,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 200

    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def create(self) -> tuple[dict, int]:
        """Create a new request based on a request type.

        The data is in the form of:
            .. code-block:: json
            {
                "request_type": "request_type",
                "topic": {
                    "type": "pid",
                    "value": "value"
                },
                ...payload
            }
        """
        # request_type = resource_requestctx.data.pop("request_type", None)
        # topic = stringify_first_val(resource_requestctx.data.pop("topic", None))
        # resolved_topic = resolve_reference_dict(topic)

        items = self.oarepo_requests_service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.data.pop("request_type", None),
            topic=(
                resolve_reference_dict(
                    stringify_first_val(resource_requestctx.data.pop("topic", None))
                )
                if resource_requestctx.data
                else None
            ),
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_view_args
    @response_handler()
    def read_extended(self) -> tuple[dict, int]:
        """Read a request on this url."""
        item = self.oarepo_requests_service.read(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 200
