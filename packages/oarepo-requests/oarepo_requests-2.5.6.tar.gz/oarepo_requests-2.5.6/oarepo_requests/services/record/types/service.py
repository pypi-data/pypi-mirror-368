#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request types service."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.base.links import Link

from oarepo_requests.services.results import RequestTypesList
from oarepo_requests.services.schema import RequestTypeSchema
from oarepo_requests.utils import allowed_request_types_for_record

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services import ServiceConfig
    from invenio_records_resources.services.records.service import RecordService

    from oarepo_requests.services.oarepo.service import OARepoRequestsService


class RecordRequestTypesService:
    """Service for request types of a record (that is, applicable request types)."""

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
        return f"{self.record_service.config.service_id}_request_types"

    @property
    def record_cls(self) -> type[Record]:
        """Return factory for creating a record class."""
        return self.record_service.config.record_cls

    def get_applicable_request_types_for_published_record(
        self, identity: Identity, record_id: str
    ) -> RequestTypesList:
        """Get applicable request types for a record given by persistent identifier."""
        record = self.record_cls.pid.resolve(record_id)  # type: ignore
        return self._get_applicable_request_types(identity, record)

    def _get_applicable_request_types(
        self, identity: Identity, record: Record
    ) -> RequestTypesList:
        """Get applicable request types for a record."""
        if not getattr(record, "is_draft", False):
            self.record_service.require_permission(identity, "read", record=record)
        else:
            self.record_service.require_permission(
                identity, "read_draft", record=record
            )
        allowed_request_types = allowed_request_types_for_record(identity, record)
        return RequestTypesList(
            service=self.record_service,
            identity=identity,
            results=list(allowed_request_types.values()),
            links_tpl=LinksTemplate(
                {"self": Link("{+record_link_requests}/applicable")}
            ),
            schema=RequestTypeSchema,
            record=record,
        )
