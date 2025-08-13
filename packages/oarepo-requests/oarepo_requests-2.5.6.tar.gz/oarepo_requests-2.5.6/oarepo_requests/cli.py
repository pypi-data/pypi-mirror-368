from oarepo_runtime.cli import oarepo
from oarepo_requests.services.escalation import check_escalations

@oarepo.group(name='requests')
def oarepo_requests():
    """OARepo requests group command."""
    pass

@oarepo_requests.command(name='escalate')
def escalate_requests():
    """Check and escalate all stale requests by changing the recipient and sending the notification to the new recipient.

    Stale request is a type of request in which original recipient did not react in time (21 days, 7 days etc.)
    """
    check_escalations()