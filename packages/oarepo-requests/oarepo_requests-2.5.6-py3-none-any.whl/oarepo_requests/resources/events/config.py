#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Resource configuration for events and comments."""

from __future__ import annotations

import importlib_metadata
import marshmallow as ma
from flask_resources import ResponseHandler
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources.events.config import RequestCommentsResourceConfig

from oarepo_requests.resources.ui import OARepoRequestEventsUIJSONSerializer


class OARepoRequestsCommentsResourceConfig(
    RequestCommentsResourceConfig, ConfiguratorMixin
):
    """Resource configuration for comments."""

    blueprint_name = "oarepo_request_events"
    url_prefix = "/requests"
    routes = {
        **RequestCommentsResourceConfig.routes,
        "list-extended": "/extended/<request_id>/comments",
        "timeline-extended": "/extended/<request_id>/timeline",
        "item-extended": "/extended/<request_id>/comments/<comment_id>",
        "event-type": "/<request_id>/timeline/<event_type>",
        "event-type-extended": "/extended/<request_id>/timeline/<event_type>",
    }

    @property
    def request_item_view_args(self):
        return {
            **super().request_item_view_args,
            "event_type": ma.fields.Str(),
        }

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:
        """Get response handlers.

        :return: Response handlers (dict of content-type -> handler)
        """
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestEventsUIJSONSerializer()
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
            group="oarepo_requests.events.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        return entrypoint_error_handlers
