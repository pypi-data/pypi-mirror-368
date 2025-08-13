from __future__ import annotations

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields


class RecordSnapshotEventType(EventType):
    """Record snapshot event type.

    Payload contain old version of the record, new version and their difference.
    """

    type_id = "S"

    payload_schema = dict(
        old_version=fields.Str(),
        new_version=fields.Str(),
        diff=fields.Str()
    )

    payload_required = True
