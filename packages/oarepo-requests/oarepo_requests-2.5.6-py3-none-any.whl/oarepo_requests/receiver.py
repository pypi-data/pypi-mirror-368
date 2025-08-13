#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default workflow receiver function."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_requests.errors import ReceiverNonReferencable, RequestTypeNotInWorkflow

if TYPE_CHECKING:
    from invenio_records_resources.records.api import Record
    from invenio_requests.customizations.request_types import RequestType
    from oarepo_workflows import WorkflowRequest

    from oarepo_requests.typing import EntityReference


def default_workflow_receiver_function(
    record: Record = None, request_type: RequestType = None, **kwargs: Any
) -> EntityReference | None:
    """Get the receiver of the request.

    This function is called by oarepo-requests when a new request is created. It should
    return the receiver of the request. The receiver is the entity that is responsible for
    accepting/declining the request.
    """
    from oarepo_workflows.proxies import current_oarepo_workflows

    workflow_id = current_oarepo_workflows.get_workflow_from_record(record)
    if not workflow_id:
        return None  # exception?

    try:
        request: WorkflowRequest = getattr(
            current_oarepo_workflows.record_workflows[workflow_id].requests(),
            request_type.type_id,
        )
    except AttributeError as e:
        raise RequestTypeNotInWorkflow(request_type.type_id, workflow_id) from e

    receiver = request.recipient_entity_reference(
        record=record, request_type=request_type, **kwargs
    )
    if not request_type.receiver_can_be_none and not receiver:
        raise ReceiverNonReferencable(
            request_type=request_type, record=record, **kwargs
        )
    return receiver
