from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder

class EscalateRequestSubmitNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    type = "escalate-request-event.submit"

    recipients = [EntityRecipient(key="request.receiver")]  # email only
