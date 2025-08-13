#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import marshmallow as ma
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.uow import RecordCommitOp, UnitOfWork
from invenio_requests.proxies import current_requests_service
from oarepo_runtime.datastreams.utils import get_record_service_for_record

from oarepo_requests.actions.publish_draft import (
    PublishDraftAcceptAction,
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)

from ..utils import classproperty
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request

    from oarepo_requests.typing import EntityReference


from invenio_access.permissions import system_identity
from invenio_requests.records.api import Request

from oarepo_requests.typing import EntityReference
from oarepo_requests.utils import get_requests_service_for_records_service

from ..errors import UnresolvedRequestsError


class PublishRequestType(NonDuplicableOARepoRequestType):
    """Publish draft request type."""

    payload_schema = {
        "published_record.links.self": ma.fields.Str(
            attribute="published_record:links:self",
            data_key="published_record:links:self",
        ),
        "published_record.links.self_html": ma.fields.Str(
            attribute="published_record:links:self_html",
            data_key="published_record:links:self_html",
        ),
    }

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": PublishDraftSubmitAction,
            "accept": PublishDraftAcceptAction,
            "decline": PublishDraftDeclineAction,
        }

    description = _("Request to publish a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    editable = False  # type: ignore

    def assert_no_pending_requests(
        self,
        topic: Record,
    ) -> None:
        topic_service = get_record_service_for_record(topic)

        request_service = get_requests_service_for_records_service(
            topic_service
        )  # , extra_filters = TermQuery(status="open")
        requests = request_service.search_requests_for_draft(
            system_identity, topic.pid.pid_value
        )

        for result in requests._results:
            # note: we can not use solely the result.is_open because changes may not be committed yet
            # to opensearch index. That's why we need to get the record from DB and re-check.
            if (
                result.is_open
                and result.type != self.type_id
                and Request.get_record(result.uuid)["status"]
                in (
                    "submitted",
                    "created",
                )
            ):
                raise UnresolvedRequestsError(action=str(self.name))

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
        if not topic.is_draft:
            raise ValueError(
                gettext("Trying to create publish request on published record")
            )
        self.assert_no_pending_requests(topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)
        self.validate_topic(identity, topic)

    @classmethod
    def validate_topic(cls, identity: Identity, topic: Record) -> None:
        """Validate the topic.

        :param: identity: identity of the caller
        :param: topic: topic of the request

        :raises: ValidationError: if the topic is not valid
        """
        topic_service = get_record_service_for_record(topic)
        topic_service.validate_draft(identity, topic["id"])

        # if files support is enabled for this topic, check if there are any files
        if hasattr(topic, "files"):
            can_toggle_files = topic_service.check_permission(
                identity, "manage_files", record=topic
            )
            draft_files = topic.files  # type: ignore
            if draft_files.enabled and not draft_files.items():
                if can_toggle_files:
                    my_message = gettext(
                        "Missing uploaded files. To disable files for this record please mark it as metadata-only."
                    )
                else:
                    my_message = gettext("Missing uploaded files.")

                raise ma.ValidationError({"files.enabled": [my_message]})

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if not topic.is_draft:
            return False
        super_ = super().is_applicable_to(identity, topic, *args, **kwargs)
        return super_

    def topic_change(self, request: Request, new_topic: dict, uow: UnitOfWork) -> None:
        """Change the topic of the request."""
        request.topic = new_topic
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))

    @classmethod
    def topic_type(
        cls, topic: Record
    ) -> (
        Literal["initial"]
        | Literal["new_version"]
        | Literal["metadata"]
        | Literal["published"]
    ):
        index = topic.versions.index
        is_latest = topic.versions.is_latest
        is_draft = topic.is_draft

        if not is_draft:
            return "published"

        if index == 1 and not is_latest:
            return "initial"
        elif index > 1 and not is_latest:
            return "new_version"
        return "metadata"
