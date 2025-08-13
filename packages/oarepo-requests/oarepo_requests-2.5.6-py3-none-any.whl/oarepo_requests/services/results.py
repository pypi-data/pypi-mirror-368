#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Results components for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.services.results import RecordList, ResultsComponent

from oarepo_requests.services.draft.service import DraftRecordRequestsService
from oarepo_requests.services.schema import RequestTypeSchema
from oarepo_requests.utils import (
    allowed_request_types_for_record,
    get_requests_service_for_records_service,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_requests.customizations.request_types import RequestType


class RequestTypesComponent(ResultsComponent):
    """Component for expanding request types."""

    def update_data(
        self, identity: Identity, record: Record, projection: dict, expand: bool
    ) -> None:
        """Expand request types if requested."""
        if not expand:
            return
        allowed_request_types = allowed_request_types_for_record(identity, record)
        request_types_list = serialize_request_types(
            allowed_request_types, identity, record
        )
        projection["expanded"]["request_types"] = request_types_list


def serialize_request_types(
    request_types: dict[str, RequestType], identity: Identity, record: Record
) -> list[dict]:
    """Serialize request types.

    :param request_types: Request types to serialize.
    :param identity: Identity of the user.
    :param record: Record for which the request types are serialized.
    :return: List of serialized request types.
    """
    request_types_list = []
    for request_type in request_types.values():
        request_types_list.append(
            serialize_request_type(request_type, identity, record)
        )
    return request_types_list


def serialize_request_type(
    request_type: RequestType, identity: Identity, record: Record
) -> dict:
    """Serialize a request type.

    :param request_type: Request type to serialize.
    :param identity: Identity of the caller.
    :param record: Record for which the request type is serialized.
    """
    return RequestTypeSchema(context={"identity": identity, "record": record}).dump(
        request_type
    )


class RequestsComponent(ResultsComponent):
    """Component for expanding requests on a record."""

    def update_data(
        self, identity: Identity, record: Record, projection: dict, expand: bool
    ) -> None:
        """Expand requests if requested."""
        if not expand:
            return

        service = get_requests_service_for_records_service(
            get_record_service_for_record(record)
        )
        reader = (
            cast(DraftRecordRequestsService, service).search_requests_for_draft
            if getattr(record, "is_draft", False)
            else service.search_requests_for_record
        )
        try:
            requests = list(reader(identity, record["id"]).hits)
        except PermissionDeniedError:
            requests = []
        projection["expanded"]["requests"] = requests


class RequestTypesListDict(dict):
    """List of request types dictionary with additional topic."""

    topic = None


class RequestTypesList(RecordList):
    """An in-memory list of request types compatible with opensearch record list."""

    def __init__(self, *args: Any, record: Record | None = None, **kwargs: Any) -> None:
        """Initialize the list of request types."""
        self._record = record
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        hits = list(self.hits)

        record_links = self._service.config.links_item
        rendered_record_links = LinksTemplate(record_links, context={}).expand(
            self._identity, self._record
        )
        links_tpl = LinksTemplate(
            self._links_tpl._links,
            context={
                **{f"record_link_{k}": v for k, v in rendered_record_links.items()}
            },
        )
        res = RequestTypesListDict(
            hits={
                "hits": hits,
                "total": self.total,
            }
        )
        if self._links_tpl:
            res["links"] = links_tpl.expand(self._identity, None)
        res.topic = self._record
        return res

    @property
    def hits(self) -> Iterator[dict]:
        """Iterator over the hits."""
        for hit in self._results:
            # Project the record
            projection = self._schema(
                context=dict(
                    identity=self._identity,
                    record=self._record,
                )
            ).dump(
                hit,
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(self._identity, hit)
            yield projection

    @property
    def total(self) -> int:
        """Total number of hits."""
        return len(self._results)
