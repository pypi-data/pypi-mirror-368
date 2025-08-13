from datetime import datetime, timezone, timedelta
from typing import Iterator
from contextlib import suppress
import json

from invenio_access.permissions import system_identity
from invenio_notifications.services.uow import NotificationOp

from invenio_requests.proxies import current_requests_service
from invenio_records_resources.services.uow import RecordCommitOp,unit_of_work
from invenio_requests.records import Request
from invenio_requests import current_events_service
from invenio_requests.records.models import RequestEventModel
from invenio_db import db

from oarepo_workflows import WorkflowRequestEscalation
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.requests import RecipientEntityReference
from oarepo_requests.types.events.escalation import EscalationEventType
from oarepo_requests.notifications.builders.escalate import EscalateRequestSubmitNotificationBuilder

import logging

@unit_of_work()
def escalate_request(request: Request, escalation: WorkflowRequestEscalation, uow=None) -> None:
    """Escalate single request and commit the change to the database."""
    logging.info(f"Escalating request {request.id}")
    resolved_topic = request.topic.resolve()
    receiver = RecipientEntityReference(request_or_escalation=escalation, record=resolved_topic)

    old_receiver_str = json.dumps(request['receiver'],sort_keys=True)
    new_receiver_str = json.dumps(receiver,sort_keys=True)
    if new_receiver_str != old_receiver_str:
        logging.info(f"Request {request.id} receiver changed from {old_receiver_str} to {new_receiver_str}")

        data = {
            "payload":
                {
                    "old_receiver": old_receiver_str,
                    "new_receiver": new_receiver_str,
                    "escalation": escalation.escalation_id,
                }
            }

        current_events_service.create(
            system_identity,
            request.id,
            data,
            event_type=EscalationEventType,
            uow=uow,
        )

        request.receiver = receiver
        request.commit()
        uow.register(
            NotificationOp(
                EscalateRequestSubmitNotificationBuilder.build(request=request)
            )
        )
        logging.info(f"Notification mail sent to {new_receiver_str}")
        uow.register(RecordCommitOp(request))



def check_escalations() -> None:
    """Check and escalate all stale requests, if after time delta is reached."""
    print("Checking for stale requests")
    for request, escalation in stale_requests():
        escalate_request(request, escalation)

def stale_requests() -> Iterator[Request]:
    """Yield all submitted requests with expired time of escalation"""
    hits = current_requests_service.scan(system_identity, params={"is_open": True})
    for hit in hits:
        #with (suppress(Exception)):
        r = Request.get_record(hit['id'])
        request_type = r.type.type_id
        topic = r.topic.resolve()
        workflow = current_oarepo_workflows.get_workflow(topic)
        workflow_request = workflow.requests()[request_type]

        if hasattr(workflow_request, "escalations") and workflow_request.escalations:
                results = db.session.query(RequestEventModel).filter(
                    RequestEventModel.type == "E",
                    RequestEventModel.request_id == r.id
                ).all()

                sorted_escalations = sorted(workflow_request.escalations, key=lambda escalation: escalation.after)
                most_recent_escalation = None

                for escalation in sorted_escalations:
                    if any(result.json['payload']['escalation'] == escalation.escalation_id for result in results):
                        continue # already processed

                    # take the most recent one
                    utc_now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
                    if r.updated + escalation.after <= utc_now_naive: # for some reason request is not timezone aware
                        most_recent_escalation = escalation
                    else:
                        break

                if most_recent_escalation:
                    yield r, most_recent_escalation
