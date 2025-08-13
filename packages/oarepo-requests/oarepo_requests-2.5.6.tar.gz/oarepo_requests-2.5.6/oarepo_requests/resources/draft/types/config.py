#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Draft request types resource configuration."""

from __future__ import annotations

from oarepo_requests.resources.record.types.config import (
    RecordRequestTypesResourceConfig,
)


class DraftRequestTypesResourceConfig(RecordRequestTypesResourceConfig):
    """Draft request types resource configuration."""

    routes = {
        **RecordRequestTypesResourceConfig.routes,
        "list-applicable-requests-draft": "/<pid_value>/draft/requests/applicable",
    }
