#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import marshmallow as ma
from invenio_requests.records.api import Request
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from invenio_i18n import gettext, lazy_gettext as _

from oarepo_requests.actions.publish_draft import (
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)
from oarepo_requests.errors import VersionAlreadyExists

from ..actions.publish_new_version import PublishNewVersionAcceptAction
from ..utils import classproperty
from .publish_base import PublishRequestType
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request

    from oarepo_requests.typing import EntityReference


class PublishNewVersionRequestType(PublishRequestType):
    """Request type for publication of a new version of a record."""

    type_id = "publish_new_version"
    name = _("Publish new version")
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

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": PublishDraftSubmitAction,
            "accept": PublishNewVersionAcceptAction,
            "decline": PublishDraftDeclineAction,
        }

    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    editable = False  # type: ignore

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if cls.topic_type(topic) != "new_version":
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
            create_autoapproved=gettext("Publish new version"),
            submit=gettext("Submit for review"),
            submitted_receiver=gettext("Review and publish new version"),
            submitted_creator=gettext("New version submitted for review"),
            submitted_others=gettext("New version submitted for review"),
            accepted=gettext("New version published"),
            declined=gettext("New version publication declined"),
            cancelled=gettext("New version publication cancelled"),
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
                "By submitting the new version for review you are requesting the publication of the new version. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            ),
            create_autoapproved=gettext(
                "Click to immediately publish the new version. "
                "The new version will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            ),
            submit=gettext(
                "Submit for review. After submitting the new version for review, "
                "it will be locked and no further modifications will be possible."
            ),
            submitted_receiver=gettext(
                "The new version has been submitted for review. "
                "You can now accept or decline the request."
            ),
            submitted_creator=gettext(
                "The new version has been submitted for review. "
                "It is now locked and no further changes are possible. "
                "You will be notified about the decision by email."
            ),
            submitted_others=gettext("The new version has been submitted for review. "),
            accepted=gettext("The new version has been published. "),
            declined=gettext("Publication of the new version has been declined."),
            cancelled=gettext("The new version has been cancelled. "),
            created=gettext("Waiting for finishing the new version publication request."),
        )

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: EntityReference,
        topic: Record,
        creator: EntityReference,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created."""
        topic_service = get_record_service_for_record(topic)
        # Only needed in case of new version as when you are publishing
        # draft for the first time, there are no previous versions with
        # which you can have collision
        if "payload" in data and "version" in data["payload"]:
            versions = topic_service.search_versions(identity, topic.pid.pid_value)
            versions_hits = versions.to_dict()["hits"]["hits"]
            for rec in versions_hits:
                if "version" in rec["metadata"]:
                    version = rec["metadata"]["version"]
                    if version == data["payload"]["version"]:
                        raise VersionAlreadyExists()

        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)
