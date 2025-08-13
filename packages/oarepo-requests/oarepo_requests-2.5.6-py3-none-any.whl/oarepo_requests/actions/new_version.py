#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for creating a new version of a published record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_requests.actions.record_snapshot_mixin import RecordSnapshotMixin
from .generic import AddTopicLinksOnPayloadMixin, OARepoAcceptAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from .components import RequestActionState
    from invenio_drafts_resources.records import Record
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.customizations import RequestType


class NewVersionAcceptAction(AddTopicLinksOnPayloadMixin, RecordSnapshotMixin, OARepoAcceptAction):
    """Accept creation of a new version of a published record."""

    self_link = "draft_record:links:self"
    self_html_link = "draft_record:links:self_html"

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Apply the action, creating a new version of the record."""
        topic_service = get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")

        new_version_topic = topic_service.new_version(identity, state.topic["id"], uow=uow)
        state.topic = new_version_topic._record
        if (
            "payload" in self.request
            and "keep_files" in self.request["payload"]
            and self.request["payload"]["keep_files"] == "yes"
        ):
            topic_service.import_files(identity, new_version_topic.id)

        if "payload" not in self.request:
            self.request["payload"] = {}
        self.request["payload"]["draft_record:id"] = new_version_topic["id"]

        return super().apply(
            identity, state, uow, *args, **kwargs
        )
