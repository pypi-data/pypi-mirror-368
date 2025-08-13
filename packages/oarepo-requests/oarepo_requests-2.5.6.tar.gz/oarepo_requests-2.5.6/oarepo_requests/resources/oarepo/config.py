#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the extended requests API."""

from __future__ import annotations

import importlib_metadata
from flask_resources import ResponseHandler
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer


class OARepoRequestsResourceConfig(RequestsResourceConfig, ConfiguratorMixin):
    """Config for the extended requests API."""

    blueprint_name = "oarepo-requests"
    url_prefix = "/requests"
    routes = {
        **RequestsResourceConfig.routes,
        "list": "/",
        "list-extended": "/extended",
        "item-extended": "/extended/<id>",
    }

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:
        """Response handlers for the extended requests API."""
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestsUIJSONSerializer()
            ),
            **super().response_handlers,
        }

    @property
    def error_handlers(self) -> dict:
        """Get error handlers."""
        entrypoint_error_handlers = {}
        for x in importlib_metadata.entry_points(
            group="oarepo_requests.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        for x in importlib_metadata.entry_points(
            group="oarepo_requests.extended.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        return entrypoint_error_handlers
