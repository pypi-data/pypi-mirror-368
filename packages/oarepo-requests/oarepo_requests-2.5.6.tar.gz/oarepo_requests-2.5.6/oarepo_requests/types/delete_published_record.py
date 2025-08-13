#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request for deleting published record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import marshmallow as ma
from oarepo_runtime.datastreams.utils import get_record_service_for_record_class
from invenio_i18n import gettext, lazy_gettext as _
from typing_extensions import override

from oarepo_requests.actions.delete_published_record import (
    DeletePublishedRecordAcceptAction,
    DeletePublishedRecordDeclineAction,
    DeletePublishedRecordSubmitAction,
)

from ..utils import classproperty, is_auto_approved, request_identity_matches
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


class DeletePublishedRecordRequestType(NonDuplicableOARepoRequestType):
    """Request type for requesting deletion of a published record."""

    type_id = "delete_published_record"
    name = _("Delete record")

    payload_schema = {
        "removal_reason": ma.fields.Str(required=True),
        "note": ma.fields.Str(),
    }

    form = [
        {
            "section": "",
            "fields": [
                {
                    "field": "removal_reason",
                    "ui_widget": "Input",
                    "props": {
                        "label": _("Removal Reason"),
                        "placeholder": _("Write down the removal reason."),
                        "required": True,
                    },
                },
                {
                    "section": "",
                    "field": "note",
                    "ui_widget": "Input",
                    "props": {
                        "label": _("Note"),
                        "placeholder": _("Write down the additional note."),
                        "required": False,
                    },
                },
            ],
        }
    ]

    editable = False

    def get_ui_redirect_url(self, request: Request, context: dict) -> str:
        if request.status == "accepted":
            topic_cls = request.topic.record_cls
            service = get_record_service_for_record_class(topic_cls)
            return service.config.links_search["self_html"].expand(None, context)

    dangerous = True

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": DeletePublishedRecordSubmitAction,
            "accept": DeletePublishedRecordAcceptAction,
            "decline": DeletePublishedRecordDeclineAction,
        }

    description = _("Request deletion of published record")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)

    @override
    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful name of the request."""
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return gettext("Request record deletion")
        match request.status:
            case "submitted":
                return gettext("Record deletion requested")
            case _:
                return gettext("Request record deletion")

    @override
    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
        if is_auto_approved(self, identity=identity, topic=topic):
            return gettext("Click to permanently delete the record.")

        if not request:
            return gettext("Request permission to delete the record.")
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return gettext(
                        "Permission to delete record requested. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return gettext(
                        "You have been asked to approve the request to permanently delete the record. "
                        "You can approve or reject the request."
                    )
                return gettext("Permission to delete record (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return gettext("Submit request to get permission to delete the record.")
                return gettext("You do not have permission to delete the record.")
