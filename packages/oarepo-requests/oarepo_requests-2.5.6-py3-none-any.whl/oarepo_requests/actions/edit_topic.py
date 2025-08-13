#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for creating a draft of published record for editing metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_requests.actions.record_snapshot_mixin import RecordSnapshotMixin
from .generic import AddTopicLinksOnPayloadMixin, OARepoAcceptAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from .components import RequestActionState
    from invenio_records_resources.services.uow import UnitOfWork


class EditTopicAcceptAction(AddTopicLinksOnPayloadMixin, RecordSnapshotMixin, OARepoAcceptAction):
    """Accept creation of a draft of a published record for editing metadata."""

    self_link = "draft_record:links:self"
    self_html_link = "draft_record:links:self_html"

    @override
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the action, creating a draft of the record for editing metadata."""
        topic_service = get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")
        state.topic = topic_service.edit(identity, state.topic["id"], uow=uow)._record
        super().apply(identity, state, uow, *args, **kwargs)
