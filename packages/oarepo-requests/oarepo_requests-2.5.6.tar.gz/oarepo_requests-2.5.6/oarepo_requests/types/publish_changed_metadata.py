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

from invenio_i18n import gettext, lazy_gettext as _
from typing_extensions import override

from .publish_base import PublishRequestType

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.records.api import Request


class PublishChangedMetadataRequestType(PublishRequestType):
    """Request type for publication of changed metadata."""

    type_id = "publish_changed_metadata"
    name = _("Publish changed metadata")

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if cls.topic_type(topic) != "metadata":
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
            create_autoapproved=gettext("Publish changed metadata"),
            submit=gettext("Submit for review"),
            submitted_receiver=gettext("Review and publish changed metadata"),
            submitted_creator=gettext("Changed metadata submitted for review"),
            submitted_others=gettext("Changed metadata submitted for review"),
            accepted=gettext("Accepted changed metadata publication"),
            declined=gettext("Declined changed metadata publication"),
            cancelled=gettext("Cancelled changed metadata publication"),
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
                "By submitting the changed metadata for review you are requesting the publication of the changed metadata. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            ),
            create_autoapproved=gettext(
                "Click to immediately publish the changed metadata. "
                "The draft will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            ),
            submit=gettext(
                "Submit for review. After submitting the changed metadata for review, "
                "it will be locked and no further modifications will be possible."
            ),
            submitted_receiver=gettext(
                "The record with changed metadata has been submitted for review. "
                "You can now accept or decline the request."
            ),
            submitted_creator=gettext(
                "The record with changed metadata has been submitted for review. "
                "It is now locked and no further changes are possible. "
                "You will be notified about the decision by email."
            ),
            submitted_others=gettext(
                "The record with changed metadata has been submitted for review. "
            ),
            accepted=gettext("Accepted changed metadata publication"),
            declined=gettext("Declined changed metadata publication"),
            cancelled=gettext("Cancelled changed metadata publication"),
            created=gettext(
                "Waiting for finishing the changed metadata publication request."
            ),
        )
