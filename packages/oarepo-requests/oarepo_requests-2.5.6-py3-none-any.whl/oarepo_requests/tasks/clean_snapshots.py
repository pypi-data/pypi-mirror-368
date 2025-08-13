from celery import shared_task
from flask import current_app
from datetime import datetime, timedelta
from invenio_db import db
from invenio_requests.records.models import RequestMetadata
from oarepo_requests.models import RecordSnapshot


@shared_task
def clean_snapshots() -> None:
    """Clean old snapshots from record_snapshots table where their request was accepted.

    By default is 365 days old snapshot are deleted."""
    days = current_app.config.get('SNAPSHOT_CLEANUP_DAYS', 365)

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    accepted_requests = db.session.query(RequestMetadata.id).filter(
        RequestMetadata.json['type'] == "accepted"
    ).subquery()

    db.session.query(RecordSnapshot).filter(
        RecordSnapshot.id.in_(accepted_requests),
        RecordSnapshot.created < cutoff_date
    ).delete(synchronize_session='fetch')

    db.session.commit()
