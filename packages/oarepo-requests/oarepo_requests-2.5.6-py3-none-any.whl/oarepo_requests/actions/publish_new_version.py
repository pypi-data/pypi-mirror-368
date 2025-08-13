#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for publishing draft requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record

    from .components import RequestActionState

from .publish_draft import PublishDraftAcceptAction


class PublishNewVersionAcceptAction(PublishDraftAcceptAction):
    """Accept action for publishing draft requests."""

    self_link = "published_record:links:self"
    self_html_link = "published_record:links:self_html"

    name = _("Publish")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""
        topic_service = get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")

        if "payload" in self.request and "version" in self.request["payload"]:
            state.topic.metadata["version"] = self.request["payload"]["version"]
            uow.register(RecordCommitOp(state.topic, indexer=topic_service.indexer))

        return super().apply(identity, state, uow, *args, **kwargs)
