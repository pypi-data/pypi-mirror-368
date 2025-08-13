#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""State change notifier."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    UnitOfWork,
    unit_of_work,
)
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from invenio_requests.proxies import current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.requests.generators import auto_request_need

from oarepo_requests.proxies import current_oarepo_requests_service

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record

# TODO: move this to a more appropriate place

def create_autorequests(identity: Identity,
    record: Record,
    uow: UnitOfWork,
    **kwargs: Any,)-> None:
    record_workflow = current_oarepo_workflows.get_workflow(record)
    for request_type_id, workflow_request in record_workflow.requests().items():
        needs = workflow_request.requester_generator.needs(
            request_type=request_type_id, record=record, **kwargs
        )
        if auto_request_need in needs:
            data = kwargs.get("data", {})
            creator_ref = ResolverRegistry.reference_identity(identity)
            request_item = current_oarepo_requests_service.create(
                system_identity,
                data=data,
                request_type=request_type_id,
                topic=record,
                creator=creator_ref,
                uow=uow,
                **kwargs,
            )
            action_obj = RequestActions.get_action(request_item._record, "submit")
            if not action_obj.can_execute():
                raise CannotExecuteActionError("submit")
            action_obj.execute(identity, uow)
            uow.register(
                RecordCommitOp(
                    request_item._record, indexer=current_requests_service.indexer
                )
            )

@unit_of_work()
def auto_request_state_change_notifier(
    identity: Identity,
    record: Record,
    prev_state: str,
    new_state: str,
    uow: UnitOfWork | None = None,
    **kwargs: Any,
) -> None:
    """Create requests that should be created automatically on state change.

    For each of the WorkflowRequest definition in the workflow of the record,
    take the needs from the generators of possible creators. If any of those
    needs is an auto_request_need, create a request for it automatically.
    """
    create_autorequests(identity, record, uow, **kwargs)
