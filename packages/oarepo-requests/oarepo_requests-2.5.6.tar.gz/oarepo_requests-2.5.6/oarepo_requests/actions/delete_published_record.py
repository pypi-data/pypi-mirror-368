#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for delete published record request."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override
from datetime import datetime

from ..notifications.builders.delete_published_record import (
    DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestSubmitNotificationBuilder, DeletePublishedRecordRequestDeclineNotificationBuilder,
)
from .cascade_events import cancel_requests_on_topic_delete
from .generic import OARepoAcceptAction, OARepoDeclineAction, OARepoSubmitAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations import RequestType

from typing import TYPE_CHECKING, Any

from invenio_db import db
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import UnitOfWork
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _

from .generic import OARepoAcceptAction, OARepoDeclineAction, OARepoSubmitAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record


if TYPE_CHECKING:
    from flask_principal import Identity
    from .components import RequestActionState
    from invenio_drafts_resources.records import Record
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.customizations import RequestType


class DeletePublishedRecordSubmitAction(OARepoSubmitAction):
    """Submit action for publishing draft requests."""

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""

        uow.register(
            NotificationOp(
                DeletePublishedRecordRequestSubmitNotificationBuilder.build(
                    request=self.request
                )
            )
        )
        return super().apply(identity, state, uow, *args, **kwargs)


class DeletePublishedRecordAcceptAction(OARepoAcceptAction):
    """Accept request for deletion of a published record and delete the record."""

    name = _("Permanently delete")

    @override
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        topic_service = get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")
        if hasattr(topic_service, "delete_record"):
            from flask import current_app
            
            oarepo_rdm = current_app.extensions['oarepo-rdm']
            resource_config = oarepo_rdm.get_api_resource_config(topic_service.id)

            citation_text = "Citation unavailable."
            if resource_config and 'text/x-iso-690+plain' in resource_config.response_handlers:
                citation_text = resource_config.response_handlers['text/x-iso-690+plain'].serializer.serialize_object(state.topic)
                    
            data = {
                'removal_reason': {'id': self.request["payload"]["removal_reason"]},
                'citation_text': citation_text,
                'note': self.request['payload'].get("note",""),
                'is_visible': True
            }
            deleted_topic = topic_service.delete_record(identity, state.topic["id"], data)._record
            db.session.commit()
            state.topic = deleted_topic
        else:
            topic_service.delete(identity, state.topic["id"], *args, uow=uow, **kwargs)
        
        uow.register(
            NotificationOp(
                DeletePublishedRecordRequestAcceptNotificationBuilder.build(
                    request=self.request
                )
            )
        )
        cancel_requests_on_topic_delete(self.request, state.topic, uow)


class DeletePublishedRecordDeclineAction(OARepoDeclineAction):
    """Decline request for deletion of a published record."""

    name = _("Keep the record")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""

        uow.register(
            NotificationOp(
                DeletePublishedRecordRequestDeclineNotificationBuilder.build(
                    request=self.request
                )
            )
        )
        return super().apply(identity, state, uow, *args, **kwargs)
