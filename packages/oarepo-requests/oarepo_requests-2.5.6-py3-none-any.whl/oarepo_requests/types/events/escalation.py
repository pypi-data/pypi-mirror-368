#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Topic update event type."""

from __future__ import annotations

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields


class EscalationEventType(EventType):
    """Comment event type."""

    type_id = "E"

    payload_schema = dict(
        old_receiver=fields.Str(),
        new_receiver=fields.Str(),
        escalation=fields.Str(),
    )

    payload_required = True
