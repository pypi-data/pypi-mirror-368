#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Helper functions for cascading request update on topic change or delete."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_access.permissions import system_identity
from invenio_requests import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.records import Request
from invenio_requests.resolvers.registry import ResolverRegistry

from oarepo_requests.utils import create_query_term_for_reference

if TYPE_CHECKING:
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.customizations import EventType
    from invenio_records_resources.records import Record
    from oarepo_requests.typing import EntityReference


def _str_from_ref(ref: EntityReference) -> str:
    k, v = next(iter(ref.items()))
    return f"{k}.{v}"


def _get_topic_reference(topic: Any) -> EntityReference:
    return ResolverRegistry.reference_entity(topic)


def _get_requests_with_topic_reference(topic_ref: EntityReference) -> list[dict]:
    requests_with_topic = current_requests_service.scan(
        system_identity,
        extra_filter=create_query_term_for_reference("topic", topic_ref),
    )
    return requests_with_topic


def _create_event(
    cur_request: Request, payload: dict, event_type: type[EventType], uow: UnitOfWork
) -> None:
    data = {"payload": payload}
    current_events_service.create(
        system_identity,
        cur_request.id,
        data,
        event_type=event_type,
        uow=uow,
    )


def update_topic(
    request: Request, old_topic: Record, new_topic: Record, uow: UnitOfWork
) -> None:
    """Update topic on all requests with the old topic to the new topic.

    :param request: Request on which the action is being executed, might be handled differently than the rest of the requests with the same topic
    :param old_topic: Old topic
    :param new_topic: New topic
    :param uow: Unit of work
    """
    from oarepo_requests.types.events import TopicUpdateEventType

    old_topic_ref = _get_topic_reference(old_topic)
    requests_with_topic = _get_requests_with_topic_reference(old_topic_ref)
    new_topic_ref = ResolverRegistry.reference_entity(new_topic)
    for (
        request_from_search
    ) in (
        requests_with_topic._results
    ):  # result list links might crash before update of the topic
        request_from_search_id = request_from_search["uuid"]
        request_type = current_request_type_registry.lookup(
            request_from_search["type"], quiet=True
        )
        if hasattr(request_type, "topic_change"):
            cur_request = (
                Request.get_record(request_from_search_id)
                if request_from_search_id != str(request.id)
                else request
            )  # request on which the action is executed is recommited later, the change must be done on the same instance
            request_type.topic_change(cur_request, new_topic_ref, uow)
            if (
                cur_request.topic.reference_dict != old_topic_ref
            ):  # what if we don't change topic but still do some event we want to log, ie. cancelling the request because it does not apply to published record
                payload = {
                    "old_topic": _str_from_ref(old_topic_ref),
                    "new_topic": _str_from_ref(new_topic_ref),
                }
                _create_event(cur_request, payload, TopicUpdateEventType, uow)


def cancel_requests_on_topic_delete(
    request: Request, topic: Record, uow: UnitOfWork
) -> None:
    """Cancel all requests with the topic that is being deleted."""
    from oarepo_requests.types.events import TopicDeleteEventType

    topic_ref = _get_topic_reference(topic)
    requests_with_topic = _get_requests_with_topic_reference(topic_ref)
    for (
        request_from_search
    ) in (
        requests_with_topic._results
    ):  # result list links might crash before update of the topic
        request_from_search_id = request_from_search["uuid"]
        request_type = current_request_type_registry.lookup(
            request_from_search["type"], quiet=True
        )
        if hasattr(request_type, "on_topic_delete"):
            if request_from_search_id == str(request.id):
                continue
            cur_request = Request.get_record(request_from_search_id)
            if cur_request.is_open:
                request_type.on_topic_delete(
                    cur_request, uow
                )  # possibly return message to save on event payload?
                payload = {"topic": _str_from_ref(topic_ref)}
                _create_event(cur_request, payload, TopicDeleteEventType, uow)
