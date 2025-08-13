#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration of oarepo-requests."""

from __future__ import annotations

import invenio_requests.config
import oarepo_workflows  # noqa
from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS as RDM_NOTIFICATIONS_BUILDERS
from invenio_notifications.backends.email import EmailNotificationBackend
from oarepo_requests.notifications.builders.delete_published_record import (
    DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestSubmitNotificationBuilder, DeletePublishedRecordRequestDeclineNotificationBuilder,
)
from oarepo_requests.notifications.builders.publish import (
    PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder, PublishDraftRequestDeclineNotificationBuilder,
)

from oarepo_requests.notifications.builders.escalate import (
    EscalateRequestSubmitNotificationBuilder,
)
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows.requests.events import WorkflowEvent

from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestIdentityComponent,
    WorkflowTransitionComponent,
)
from oarepo_requests.notifications.generators import (
    GroupEmailRecipient,
    MultipleRecipientsEmailRecipients,
    UserEmailRecipient,
)
from oarepo_requests.resolvers.ui import (
    AutoApproveUIEntityResolver,
    FallbackEntityReferenceUIResolver,
    GroupEntityReferenceUIResolver,
    UserEntityReferenceUIResolver,
)
from oarepo_requests.resolvers.user_notification_resolver import (
    UserNotificationResolver,
)
from oarepo_requests.types import (
    DeletePublishedRecordRequestType,
    EditPublishedRecordRequestType,
    PublishDraftRequestType,
)
from oarepo_requests.types.events import TopicDeleteEventType
from oarepo_requests.types.events.escalation import EscalationEventType
from oarepo_requests.types.events.record_snapshot import RecordSnapshotEventType
from oarepo_requests.types.events.topic_update import TopicUpdateEventType

REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    PublishDraftRequestType(),
]

REQUESTS_REGISTERED_EVENT_TYPES = [
    TopicUpdateEventType(),
    TopicDeleteEventType(),
    EscalationEventType(),
    RecordSnapshotEventType(),
] + invenio_requests.config.REQUESTS_REGISTERED_EVENT_TYPES

REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

DEFAULT_WORKFLOW_EVENTS = {
    CommentEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    LogEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    TopicUpdateEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    TopicDeleteEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    EscalationEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    RecordSnapshotEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
}


ENTITY_REFERENCE_UI_RESOLVERS = {
    "user": UserEntityReferenceUIResolver("user"),
    "fallback": FallbackEntityReferenceUIResolver("fallback"),
    "group": GroupEntityReferenceUIResolver("group"),
    "auto_approve": AutoApproveUIEntityResolver("auto_approve"),
}

REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]

workflow_action_components = [WorkflowTransitionComponent]

REQUESTS_ACTION_COMPONENTS = {
    "accepted": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "submitted": [
        AutoAcceptComponent,  # AutoAcceptComponent must always be first, so that auto accept is called as the last step in action handling
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "declined": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "cancelled": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "expired": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
}

NOTIFICATION_RECIPIENTS_RESOLVERS = {
    "user": {"email": UserEmailRecipient},
    "group": {"email": GroupEmailRecipient},
    "multiple": {"email": MultipleRecipientsEmailRecipients},
}

SNAPSHOT_CLEANUP_DAYS = 365

PUBLISH_REQUEST_TYPES = ["publish_draft", "publish_new_version"]

NOTIFICATIONS_ENTITY_RESOLVERS = [
    UserNotificationResolver(),
    ServiceResultResolver(service_id="requests", type_key="request"),
    ServiceResultResolver(service_id="request_events", type_key="request_event"),
]

NOTIFICATIONS_BACKENDS = {
    EmailNotificationBackend.id: EmailNotificationBackend(),
}

NOTIFICATIONS_BUILDERS = {
    **RDM_NOTIFICATIONS_BUILDERS,
    DeletePublishedRecordRequestSubmitNotificationBuilder.type: DeletePublishedRecordRequestSubmitNotificationBuilder,
    DeletePublishedRecordRequestAcceptNotificationBuilder.type: DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestDeclineNotificationBuilder.type: DeletePublishedRecordRequestDeclineNotificationBuilder,
    EscalateRequestSubmitNotificationBuilder.type: EscalateRequestSubmitNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder.type: PublishDraftRequestSubmitNotificationBuilder,
    PublishDraftRequestAcceptNotificationBuilder.type: PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestDeclineNotificationBuilder.type: PublishDraftRequestDeclineNotificationBuilder,
}