#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Draft record requests service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.uow import unit_of_work
from invenio_search.engine import dsl

from oarepo_requests.services.record.service import RecordRequestsService
from oarepo_requests.utils import get_entity_key_for_record_cls

if TYPE_CHECKING:
    from datetime import datetime

    from flask_principal import Identity
    from invenio_drafts_resources.records.api import Record
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.services.requests.results import RequestItem
    from opensearch_dsl.query import Query


class DraftRecordRequestsService(RecordRequestsService):
    """Draft record requests service."""

    @property
    def draft_cls(self) -> type[Record]:
        """Factory for creating a record class."""
        return self.record_service.config.draft_cls

    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_draft(
        self,
        identity: Identity,
        record_id: str,
        params: dict[str, str] | None = None,
        search_preference: Any = None,
        expand: bool = False,
        extra_filter: Query | None = None,
        **kwargs: Any,
    ) -> RequestItem:
        """Search for record's requests."""
        record = self.draft_cls.pid.resolve(record_id, registered_only=False)
        self.record_service.require_permission(identity, "read_draft", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q(
                    "term",
                    **{
                        f"topic.{get_entity_key_for_record_cls(self.draft_cls)}": record_id
                    },
                ),
            ],
        )
        if extra_filter is not None:
            search_filter = search_filter & extra_filter

        return self.requests_service.search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=search_filter,
            **kwargs,
        )

    @unit_of_work()
    def create_for_draft(
        self,
        identity: Identity,
        data: dict,
        request_type: str,
        topic_id: str,
        expires_at: datetime | None = None,
        uow: UnitOfWork | None = None,
        expand: bool = False,
    ) -> RequestItem:
        """Create a request on a draft record."""
        record = self.draft_cls.pid.resolve(topic_id, registered_only=False)
        return self.oarepo_requests_service.create(
            identity=identity,
            data=data,
            request_type=request_type,
            topic=record,
            expand=expand,
            uow=uow,
        )
