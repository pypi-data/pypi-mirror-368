#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Blueprints for the app and events views."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask


def create_app_blueprint(app: Flask) -> Blueprint:
    """Create a blueprint for the requests endpoint.

    :param app: Flask application
    """
    blueprint = Blueprint("oarepo_requests_app", __name__, url_prefix="/requests/")
    return blueprint


def create_app_events_blueprint(app: Flask) -> Blueprint:
    """Create a blueprint for the requests events endpoint.

    :param app: Flask application
    """
    blueprint = Blueprint(
        "oarepo_requests_events_app", __name__, url_prefix="/requests/"
    )
    return blueprint


def create_notifications(app: Flask) -> Blueprint:
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "oarepo_notifications",
        __name__,
        template_folder=Path(__file__).parent.parent / "templates",
    )
    from oarepo_requests.invenio_patches import (
        override_invenio_notifications,
    )

    # adding notification patches for celery
    blueprint.record_once(override_invenio_notifications)

    return blueprint
