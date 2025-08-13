#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""API views."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask


def create_oarepo_requests(app: Flask) -> Blueprint:
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.requests_resource.as_blueprint()

    from oarepo_requests.invenio_patches import (
        override_invenio_notifications,
        override_invenio_requests_config,
    )

    blueprint.record_once(override_invenio_requests_config)
    # notification patches need to be added separately because this part
    # is not called in celery. See app.py which is called in celery
    blueprint.record_once(override_invenio_notifications)

    return blueprint


def create_oarepo_requests_events(app: Flask) -> Blueprint:
    """Create events blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.request_events_resource.as_blueprint()
    return blueprint


def create_notifications(app: Flask) -> Blueprint:
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "oarepo_notifications",
        __name__,
        template_folder=Path(__file__).parent.parent / "templates",
    )

    return blueprint
