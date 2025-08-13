from __future__ import annotations

from typing import Any, TYPE_CHECKING

import jsonpatch
from jsonpointer import resolve_pointer
from oarepo_requests.models import RecordSnapshot
from oarepo_requests.types.events.record_snapshot import RecordSnapshotEventType
from invenio_db import db
from invenio_records_resources.services.uow import unit_of_work
import json
from invenio_requests import current_events_service
from invenio_access.permissions import system_identity

if TYPE_CHECKING:
    from invenio_drafts_resources.records import Record
    from sqlalchemy_utils.types import UUIDType


@unit_of_work()
def create_snapshot_and_possible_event(topic: Record, record_metadata: dict, request_id: UUIDType, uow=None) -> None:
    """Creates new snapshot of a record and create possible event with old version, new version and difference between versions.
    
    :param Record topic: New topic to take snapshot of
    :param UUIDType request_id: Request id for given topic
    :param Any record_item: Record item with metadata, could be retrieved with service.read/read_draft(identity, topic.pid.pid_value), where service = get_record_service_for_record(topic)
    :param UnitOfWork uow: Unit of work to use (invenio)
    """
    RecordSnapshot.create(record_uuid=topic.id, request_id=request_id, json=record_metadata)
    db.session.commit()

    # go through table, filter latest two
    # if two -> create event
    results = (db.session.query(RecordSnapshot)
               .filter_by(record_uuid=topic.id)
               .order_by(RecordSnapshot.created.desc())
               .limit(2)
               .all())

    if len(results) == 2:
        old_version = results[1].json
        new_version = record_metadata
        diff = jsonpatch.JsonPatch.from_diff(old_version, new_version).patch
        diff = [op for op in diff if '@v' not in op['path']]

        for op in diff:
            if op['op'] == 'remove' or op['op'] == 'replace':
                op['old_value'] = resolve_pointer(old_version, op['path'])

        data = {
            'payload': {
                'old_version': json.dumps(old_version),
                'new_version': json.dumps(new_version),
                'diff': json.dumps(diff)
            }
        }

        current_events_service.create(
            system_identity,
            request_id,
            data,
            event_type=RecordSnapshotEventType,
            uow=uow,
        )
