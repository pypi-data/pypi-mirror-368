#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request for deleting draft records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_runtime.datastreams.utils import get_record_service_for_record_class
from invenio_i18n import gettext, lazy_gettext as _
from typing_extensions import override

from ..actions.delete_draft import DeleteDraftAcceptAction
from ..utils import classproperty, is_auto_approved, request_identity_matches
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


class DeleteDraftRequestType(NonDuplicableOARepoRequestType):
    """Request type for deleting draft records."""

    type_id = "delete_draft"
    name = _("Delete draft")

    dangerous = True

    def get_ui_redirect_url(self, request: Request, context: dict) -> str:
        if request.status == "accepted":
            topic_cls = request.topic.record_cls
            service = get_record_service_for_record_class(topic_cls)
            return service.config.links_search["self_html"].expand(None, context)

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "accept": DeleteDraftAcceptAction,
        }

    description = _("Request deletion of draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)

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
            return gettext("Request draft deletion")
        match request.status:
            case "submitted":
                return gettext("Draft deletion requested")
            case _:
                return gettext("Request draft deletion")

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
            return gettext("Click to permanently delete the draft.")

        if not request:
            return gettext("Request permission to delete the draft.")
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return gettext(
                        "Permission to delete draft requested. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return gettext(
                        "You have been asked to approve the request to permanently delete the draft. "
                        "You can approve or reject the request."
                    )
                return gettext("Permission to delete draft (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return gettext("Submit request to get permission to delete the draft.")
                return gettext("You do not have permission to delete the draft.")
