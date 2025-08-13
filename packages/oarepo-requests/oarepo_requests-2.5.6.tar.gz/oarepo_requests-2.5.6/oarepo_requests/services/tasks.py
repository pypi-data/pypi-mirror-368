from celery import shared_task
from oarepo_requests.services.escalation import check_escalations

@shared_task(name='escalate-requests')
def escalate_requests_task():
    check_escalations()