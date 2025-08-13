import logging
from datetime import datetime

import sqlalchemy as sa
from invenio_db import db
from invenio_requests.records.models import RequestMetadata
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy_utils.types import JSONType, UUIDType

logger = logging.getLogger("record-snapshot-table")


class RecordSnapshot(db.Model):
    """Store records snapshots.

    It is possible that single record can have multiple snapshots.
    """

    __tablename__ = "record_snapshots"

    __table_args__ = (
        # TODO
    )

    id = db.Column(db.Integer, primary_key=True)
    """Id of row in table."""

    record_uuid = db.Column(UUIDType, nullable=False)
    """Snapshot record UUID."""

    json = db.Column(
        db.JSON()
        .with_variant(
            postgresql.JSONB(none_as_null=True),
            "postgresql",
        )
        .with_variant(
            JSONType(),
            "sqlite",
        )
        .with_variant(
            JSONType(),
            "mysql",
        ),
        default=lambda: dict(),
        nullable=False,
    )
    """JSON with current snapshot of the record."""

    request_id = db.Column(
        UUIDType, db.ForeignKey(RequestMetadata.id, ondelete="cascade"), nullable=True
    )
    """Request ID when snapshot is made."""

    request = db.relationship(RequestMetadata, foreign_keys=[request_id])
    """Relationship between RequestMetadata table."""

    created = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, record_uuid, request_id, json):
        """Create new snapshot."""
        try:
            with db.session.begin_nested():
                obj = cls(record_uuid=record_uuid, request_id=request_id, json=json)
                db.session.add(obj)
            logger.info(
                "Created record snapshot for record uuid {record_uuid} with json {json}"
            )

        except IntegrityError:
            logger.exception(
                "Already exists",
                extra={"record_uuid": record_uuid, "json": json},
            )
            raise
        except SQLAlchemyError:
            logger.exception(
                "Failed to create record snapshot for record uuid {record_uuid}",
                extra={"json": json},
            )
            raise

        return obj

    @classmethod
    def get(cls, record_uuid):
        """Get one snapshot for given record_uuid."""
        try:
            return db.session.query(cls).filter_by(record_uuid=record_uuid).one()
        except NoResultFound:
            raise ValueError(f"No record snapshot for record uuid {record_uuid}")

    @classmethod
    def get_all(cls, record_uuid):
        """Get all snapshot for given record_uuid."""
        try:
            return db.session.query(cls).filter_by(record_uuid=record_uuid).all()
        except NoResultFound:
            raise ValueError(f"No record snapshots for record uuid {record_uuid}")

    @classmethod
    def get_two_latest_snapshots_by_record_uuid(cls, record_uuid):
        """Get latest two snapshot for record_uuid."""
        try:
            return (
                db.session.query(cls)
                .filter_by(record_uuid=record_uuid)
                .order_by(cls.created.desc())
                .limit(2)
                .all()
            )
        except NoResultFound:
            raise ValueError(f"No record snapshot for record uuid {record_uuid}")
