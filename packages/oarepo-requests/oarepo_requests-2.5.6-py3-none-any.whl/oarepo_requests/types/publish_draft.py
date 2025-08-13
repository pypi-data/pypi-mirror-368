#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import marshmallow as ma
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _
from typing_extensions import override

from .publish_base import PublishRequestType

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record

from invenio_requests.records.api import Request


class PublishDraftRequestType(PublishRequestType):
    """Publish draft request type."""

    type_id = "publish_draft"
    name = _("Publish draft")

    payload_schema = {
        **PublishRequestType.payload_schema,
        "version": ma.fields.Str(),
    }

    form = {
        "field": "version",
        "ui_widget": "Input",
        "props": {
            "label": _("Resource version"),
            "placeholder": _("Write down the version (first, second…)."),
            "required": False,
        },
    }

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if cls.topic_type(topic) != "initial":
            return False

        return super().is_applicable_to(identity, topic, *args, **kwargs)

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
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=gettext("Submit for review"),
            create_autoapproved=gettext("Publish draft"),
            submit=gettext("Submit for review"),
            submitted_receiver=gettext("Review and publish draft"),
            submitted_creator=gettext("Draft submitted for review"),
            submitted_others=gettext("Draft submitted for review"),
            accepted=gettext("Draft published"),
            declined=gettext("Draft publication declined"),
            cancelled=gettext("Draft publication cancelled"),
            created=gettext("Submit for review"),
        )

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
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=gettext(
                "By submitting the draft for review you are requesting the publication of the draft. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            ),
            create_autoapproved=gettext(
                "Click to immediately publish the draft. "
                "The draft will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            ),
            submit=gettext(
                "Submit for review. After submitting the draft for review, "
                "it will be locked and no further modifications will be possible."
            ),
            submitted_receiver=gettext(
                "The draft has been submitted for review. "
                "You can now accept or decline the request."
            ),
            submitted_creator=gettext(
                "The draft has been submitted for review. "
                "It is now locked and no further changes are possible. "
                "You will be notified about the decision by email."
            ),
            submitted_others=gettext("The draft has been submitted for review. "),
            accepted=gettext("The draft has been published. "),
            declined=gettext("Publication of the draft has been declined."),
            cancelled=gettext("The draft has been cancelled. "),
            created=gettext("Waiting for finishing the draft publication request."),
        )
