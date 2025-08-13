#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for applicable request types for a record resource."""

from __future__ import annotations

from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers

from oarepo_requests.resources.ui import OARepoRequestTypesUIJSONSerializer


class RecordRequestTypesResourceConfig:
    """Config for applicable request types for a record resource.

    Note: this config is merged with the configuration of a record on top of which
    the request types resource lives.
    """

    blueprint_name: str | None = (
        None  # will be merged from the record's resource config
    )

    routes = {
        "list-applicable-requests": "/<pid_value>/requests/applicable",
    }

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:
        """Response handlers for the record request types resource."""
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestTypesUIJSONSerializer()
            ),
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        }
