#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request needs."""

from __future__ import annotations

from invenio_access.permissions import SystemRoleNeed

request_active = SystemRoleNeed("request")
"""Need that is added to identity whenever a request is being handled (inside the 'accept' action)."""
