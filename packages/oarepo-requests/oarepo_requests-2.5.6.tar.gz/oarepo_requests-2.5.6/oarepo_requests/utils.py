#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Utility functions for the requests module."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Callable

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PersistentIdentifierError
from invenio_records_resources.proxies import current_service_registry
from invenio_requests.proxies import (
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl
from oarepo_workflows import (
    AutoApprove,
    Workflow,
    WorkflowRequest,
    WorkflowRequestPolicy,
)
from oarepo_workflows.errors import MissingWorkflowError
from oarepo_workflows.proxies import current_oarepo_workflows

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_records_resources.services import RecordService
    from invenio_requests.customizations.request_types import RequestType
    from invenio_requests.records.api import Request
    from opensearch_dsl.query import Query

    from oarepo_requests.typing import EntityReference

    from .services.record.service import RecordRequestsService


class classproperty[T]:
    """Class property decorator as decorator chaining for declaring class properties was deprecated in python 3.11."""

    def __init__(self, func: Callable):
        """Initialize the class property."""
        self.fget = func

    def __get__(self, instance: Any, owner: Any) -> T:
        """Get the value of the class property."""
        return self.fget(owner)


def allowed_request_types_for_record(
    identity: Identity, record: Record
) -> dict[str, RequestType]:
    """Return allowed request types for the record.

    If there is a workflow defined on the record, only request types allowed by the workflow are returned.

    :param identity: Identity of the user. Only the request types for which user can create a request are returned.
    :param record: Record to get allowed request types for.
    :return: Dict of request types allowed for the record.
    """
    workflow_requests: WorkflowRequestPolicy | None
    try:
        workflow_requests = current_oarepo_workflows.get_workflow(record).requests()
        return {
            type_id: wr.request_type
            for (type_id, wr) in workflow_requests.applicable_workflow_requests(
                identity, record=record
            )
        }
    except MissingWorkflowError:
        # workflow not defined on the record, probably not a workflow-enabled record
        # so returning all matching request types
        pass

    record_ref = list(ResolverRegistry.reference_entity(record).keys())[0]

    ret = {}
    for rt in current_request_type_registry:
        if record_ref in rt.allowed_topic_ref_types:
            ret[rt.type_id] = rt

    return ret


def create_query_term_for_reference(
    field_name: str, reference: EntityReference
) -> Query:
    """Create an opensearch query term for the reference.

    :param field_name: Field name to search in (can be "topic", "receiver", ...).
    :param reference: Reference to search for.
    :return: Opensearch query term.
    """
    return dsl.Q(
        "term",
        **{f"{field_name}.{list(reference.keys())[0]}": list(reference.values())[0]},
    )


def search_requests_filter(
    type_id: str,
    topic_reference: dict | None = None,
    receiver_reference: dict | None = None,
    creator_reference: dict | None = None,
    is_open: bool | None = None,
) -> Query:
    """Create a search filter for requests of a given request type.

    :param type_id: Request type id.
    :param topic_reference: Reference to the topic, optional
    :param receiver_reference: Reference to the receiver, optional
    :param creator_reference: Reference to the creator, optional
    :param is_open: Whether the request is open or closed. If not set, both open and closed requests are returned.
    """
    must = [
        dsl.Q("term", **{"type": type_id}),
    ]
    if is_open is not None:
        must.append(dsl.Q("term", **{"is_open": is_open}))
    if receiver_reference:
        must.append(create_query_term_for_reference("receiver", receiver_reference))
    if creator_reference:
        must.append(create_query_term_for_reference("creator", creator_reference))
    if topic_reference:
        must.append(create_query_term_for_reference("topic", topic_reference))

    extra_filter = dsl.query.Bool(
        "must",
        must=must,
    )

    return extra_filter


def open_request_exists(
    topic_or_reference: Record | EntityReference, type_id: str
) -> bool:
    """Check if there is an open request of a given type for the topic.

    :param topic_or_reference: Topic record or reference to the record in the form {"datasets": "id"}.
    :param type_id: Request type id.
    """
    topic_reference = ResolverRegistry.reference_entity(topic_or_reference, raise_=True)
    base_filter = search_requests_filter(
        type_id=type_id, topic_reference=topic_reference, is_open=True
    )
    results = current_requests_service.search(
        system_identity, extra_filter=base_filter
    ).hits
    request_exists = bool(list(results))
    return request_exists


def resolve_reference_dict(reference_dict: EntityReference) -> Record:
    """Resolve the reference dict to the entity (such as Record, User, ...)."""
    return ResolverRegistry.resolve_entity_proxy(reference_dict).resolve()


def get_matching_service_for_refdict(
    reference_dict: EntityReference,
) -> RecordService | None:
    """Get the service that is responsible for entities matching the reference dict.

    :param reference_dict: Reference dict in the form {"datasets": "id"}.
    :return: Service that is responsible for the entity or None if the entity does not have an associated service
    """
    for resolver in ResolverRegistry.get_registered_resolvers():
        if resolver.matches_reference_dict(reference_dict):
            return current_service_registry.get(resolver._service_id)
    return None


def get_entity_key_for_record_cls(record_cls: type[Record]) -> str:
    """Get the entity type id for the record_cls.

    :param record_cls: Record class.
    :return: Entity type id
    """
    for resolver in ResolverRegistry.get_registered_resolvers():
        if hasattr(resolver, "record_cls") and resolver.record_cls == record_cls:
            return resolver.type_id
    raise AttributeError(
        f"Record class {record_cls} does not have a registered entity resolver."
    )


def get_requests_service_for_records_service(
    records_service: RecordService,
) -> RecordRequestsService:
    """Get the requests service for the records service.

    :param records_service: Records service.
    :return: Requests service for the records service.
    """
    return current_service_registry.get(f"{records_service.config.service_id}_requests")


def stringify_first_val[T](dct: T) -> T:
    """Convert the top-level value in a dictionary to string.

    Does nothing if the value is not a dictionary.

    :param dct: Dictionary to convert (or a value of any other type).
    :return dct with the top-level value converted to string.
    """
    if isinstance(dct, dict):
        for k, v in dct.items():
            dct[k] = str(v)
    return dct


def reference_to_tuple(reference: EntityReference) -> tuple[str, str]:
    """Convert the reference dict to a tuple.

    :param reference: Reference dict in the form {"datasets": "id"}.
    :return: Tuple in the form ("datasets", "id").
    """
    return next(iter(reference.items()))


# TODO: consider moving to oarepo-workflows
def get_receiver_for_request_type(
    request_type: RequestType, identity: Identity, topic: Record
) -> EntityReference | None:
    """Get the default receiver for the request type, identity and topic.

    This call gets the workflow from the topic, looks up the request inside the workflow
    and evaluates workflow recipients for the request and topic and returns them.
    If the request has no matching receiver, None is returned.

    :param request_type: Request type.
    :param identity: Identity of the caller who wants to create a request of this type
    :param topic: Topic record for the request
    :return: Receiver for the request type from workflow or None if no receiver
    """
    if not topic:
        return None

    try:
        workflow: Workflow = current_oarepo_workflows.get_workflow(topic)
    except MissingWorkflowError:
        return None

    try:
        workflow_request: WorkflowRequest = workflow.requests()[request_type.type_id]
    except KeyError:
        return None

    receivers = workflow_request.recipient_entity_reference(
        identity=identity, record=topic, request_type=request_type, creator=identity
    )
    if not receivers:
        return None

    return receivers


# TODO: consider moving to oarepo-workflows
def is_auto_approved(
    request_type: RequestType,
    *,
    identity: Identity,
    topic: Record,
) -> bool:
    """Check if the request should be auto-approved.

    If identity creates a request of the given request type on the given topic,
    the function checks if the request should be auto-approved.
    """
    if not current_oarepo_workflows:
        return False

    receiver = get_receiver_for_request_type(
        request_type=request_type, identity=identity, topic=topic
    )

    return bool(
        receiver
        and (
            isinstance(receiver, AutoApprove)
            or isinstance(receiver, dict)
            and receiver.get("auto_approve")
        )
    )


def request_identity_matches(
    entity_reference: EntityReference, identity: Identity
) -> bool:
    """Check if the identity matches the entity reference.

    Identity matches the entity reference if the needs provided by the entity reference
    intersect with the needs provided by the identity. For example, if the entity reference
    provides [CommunityRoleNeed(comm_id, 'curator'), ActionNeed("administration")] and the
    identity provides [CommunityRoleNeed(comm_id, 'curator')], the function returns True.

    :param entity_reference: Entity reference in the form {"datasets": "id"}.
    :param identity:         Identity to check.
    """
    if not entity_reference:
        return False

    try:
        if isinstance(entity_reference, dict):
            entity = ResolverRegistry.resolve_entity_proxy(entity_reference)
        else:
            entity = entity_reference
        if entity:
            needs = entity.get_needs()
            return bool(identity.provides.intersection(needs))
    except PersistentIdentifierError:
        return False
    return False


def merge_resource_configs[T](config_to_merge_in: T, original_config: Any) -> T:
    """Merge resource configurations."""
    actual_config = copy.deepcopy(config_to_merge_in)
    original_keys = {x for x in dir(original_config) if not x.startswith("_")}
    merge_in_keys = {
        x for x in dir(config_to_merge_in) if not x.startswith("_")
    }  # have to do this bc hasattr fails on resolving response_handlers
    for copy_from_original_key in original_keys - merge_in_keys:
        setattr(
            actual_config,
            copy_from_original_key,
            getattr(original_config, copy_from_original_key),
        )
    return actual_config


def has_rights_to_accept_request(request: Request, identity: Identity) -> bool:
    """Check if the identity has rights to accept the request.

    :param request: Request to check.
    :param identity: Identity to check.
    """
    return current_requests_service.check_permission(
        identity,
        "action_accept",
        request=request,
        record=request.topic,
        request_type=request.type,
    )


def has_rights_to_submit_request(request: Request, identity: Identity) -> bool:
    """Check if the identity has rights to submit the request.

    :param request: Request to check.
    :param identity: Identity to check.
    """
    return current_requests_service.check_permission(
        identity,
        "action_submit",
        request=request,
        record=request.topic,
        request_type=request.type,
    )
