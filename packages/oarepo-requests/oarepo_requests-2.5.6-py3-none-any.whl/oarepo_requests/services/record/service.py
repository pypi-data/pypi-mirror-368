#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Record requests service."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.uow import unit_of_work
from invenio_search.engine import dsl

from oarepo_requests.proxies import current_oarepo_requests
from oarepo_requests.utils import get_entity_key_for_record_cls

if TYPE_CHECKING:
    from datetime import datetime

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services import ServiceConfig
    from invenio_records_resources.services.records.results import (
        RecordItem,
        RecordList,
    )
    from invenio_records_resources.services.records.service import RecordService
    from invenio_records_resources.services.uow import UnitOfWork
    from opensearch_dsl.query import Query

    from oarepo_requests.services.oarepo.service import OARepoRequestsService


class RecordRequestsService:
    """Service for record requests."""

    def __init__(
        self,
        record_service: RecordService,
        oarepo_requests_service: OARepoRequestsService,
    ) -> None:
        """Initialize the service."""
        self.record_service = record_service
        self.oarepo_requests_service = oarepo_requests_service

    # so api doesn't fall apart
    @property
    def config(self) -> ServiceConfig:
        """Return a dummy config."""
        return SimpleNamespace(service_id=self.service_id)  # type: ignore

    @property
    def service_id(self) -> str:
        """Return the service ID."""
        return f"{self.record_service.config.service_id}_requests"

    @property
    def record_cls(self) -> type[Record]:
        """Return factory for creating a record class."""
        return self.record_service.config.record_cls

    @property
    def requests_service(self) -> OARepoRequestsService:
        """Factory for creating a record class."""
        return current_oarepo_requests.requests_service

    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_record(
        self,
        identity: Identity,
        record_id: str,
        params: dict[str, Any] | None = None,
        search_preference: Any | None = None,
        expand: bool = False,
        extra_filter: Query | None = None,
        **kwargs: Any,
    ) -> RecordList:
        """Search for record's requests."""
        record = self.record_cls.pid.resolve(record_id)  # type: ignore
        self.record_service.require_permission(identity, "read", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q(
                    "term",
                    **{
                        f"topic.{get_entity_key_for_record_cls(self.record_cls)}": record_id
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
    def create(
        self,
        identity: Identity,
        data: dict[str, Any],
        request_type: str,
        topic_id: str,
        expires_at: datetime | None = None,
        uow: UnitOfWork | None = None,
        expand: bool = False,
    ) -> RecordItem:
        """Create a request for a record."""
        record = self.record_cls.pid.resolve(topic_id)  # type: ignore
        return self.oarepo_requests_service.create(
            identity=identity,
            data=data,
            request_type=request_type,
            topic=record,
            expand=expand,
            uow=uow,
        )
