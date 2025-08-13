#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration of the draft record requests resource."""

from __future__ import annotations

import importlib_metadata

from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """Configuration of the draft record requests resource."""

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests-draft": "/<pid_value>/draft/requests",
        "request-type-draft": "/<pid_value>/draft/requests/<request_type>",
    }

    @property
    def error_handlers(self) -> dict:
        """Get error handlers."""
        entrypoint_error_handlers = {**super().error_handlers}
        for x in importlib_metadata.entry_points(
            group="oarepo_requests.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        for x in importlib_metadata.entry_points(
            group="oarepo_requests.draft.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        return entrypoint_error_handlers
