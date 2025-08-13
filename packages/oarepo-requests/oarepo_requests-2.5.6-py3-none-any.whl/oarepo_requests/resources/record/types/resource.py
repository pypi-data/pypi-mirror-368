#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""API resource for applicable request types for a record."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from flask_resources.resources import Resource
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import request_view_args

from oarepo_requests.utils import merge_resource_configs

if TYPE_CHECKING:
    from invenio_records_resources.resources.records import RecordResourceConfig

    from ....services.record.types.service import RecordRequestTypesService
    from .config import RecordRequestTypesResourceConfig


class RecordRequestTypesResource(ErrorHandlersMixin, Resource):
    """API resource for applicable request types for a record."""

    def __init__(
        self,
        record_requests_config: RecordRequestTypesResourceConfig,
        config: RecordResourceConfig,
        service: RecordRequestTypesService,
    ) -> None:
        """Initialize the resource.

        :param config: main record resource config
        :param service:
        :param record_requests_config: config specific for the record request serivce
        """
        record_requests_config.blueprint_name = (
            f"{config.blueprint_name}_applicable_requests"
        )
        actual_config = merge_resource_configs(
            config_to_merge_in=record_requests_config, original_config=config
        )
        super().__init__(actual_config)
        self.service = service

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route(
                "GET",
                routes["list-applicable-requests"],
                self.get_applicable_request_types,
            )
        ]
        return url_rules

    @request_view_args
    @response_handler(many=True)
    def get_applicable_request_types(self) -> tuple[dict, int]:
        """List request types."""
        hits = self.service.get_applicable_request_types_for_published_record(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
        )
        return hits.to_dict(), 200
