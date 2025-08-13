#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Views for the UI (pages and form config for requests)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oarepo_ui.resources.resource import FormConfigResource

from oarepo_requests.ui.config import (
    RequestsFormConfigResourceConfig,
    RequestUIResourceConfig,
)
from oarepo_requests.ui.resource import RequestUIResource

if TYPE_CHECKING:
    from flask import Blueprint, Flask


def create_blueprint(app: Flask) -> Blueprint:
    """Register blueprint for this resource."""
    return RequestUIResource(RequestUIResourceConfig()).as_blueprint()


def create_requests_form_config_blueprint(app: Flask) -> Blueprint:
    """Register blueprint for form config resource."""
    return FormConfigResource(RequestsFormConfigResourceConfig()).as_blueprint()
