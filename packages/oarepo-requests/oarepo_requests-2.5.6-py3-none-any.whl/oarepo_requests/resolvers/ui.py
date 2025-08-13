#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""UI resolvers of common entities."""

from __future__ import annotations

import abc
import contextlib
import copy
import json
from typing import TYPE_CHECKING, Any, TypedDict, cast, override

from flask import request
from invenio_records_resources.resources.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from oarepo_runtime.i18n import gettext as _

from ..proxies import current_oarepo_requests
from ..utils import get_matching_service_for_refdict
from invenio_rdm_records.services.errors import RecordDeletedException

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.services.records import RecordService as DraftsService
    from invenio_records_resources.services.records.results import RecordItem

    from oarepo_requests.typing import EntityReference


class UIResolvedReference(TypedDict):
    """Resolved UI reference."""

    reference: EntityReference
    type: str
    label: str | LazyString
    links: dict[str, str]


def resolve(identity: Identity, reference: dict[str, str]) -> UIResolvedReference:
    """Resolve a reference to a UI representation.

    :param identity: Identity of the user.
    :param reference: Reference to resolve.
    """
    reference_type, reference_value = next(iter(reference.items()))

    # use cache to avoid multiple resolve for the same reference within one request
    # the runtime error is risen when we are outside the request context - in this case we just skip the cache
    with contextlib.suppress(RuntimeError):
        if not hasattr(request, "current_oarepo_requests_ui_resolve_cache"):
            request.current_oarepo_requests_ui_resolve_cache = {}
        cache = request.current_oarepo_requests_ui_resolve_cache
        if (reference_type, reference_value) in cache:
            return cache[(reference_type, reference_value)]

    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers

    if reference_type == "multiple":
        # TODO(mirekys): add test coverage
        resolved = []
        reference_values_list = list(json.loads(reference_value))

        for reference_values_item in reference_values_list:
            for key, value in reference_values_item.items():
                resolved.append(entity_resolvers[key].resolve_one(identity, value))
    elif reference_type in entity_resolvers:
        resolved = entity_resolvers[reference_type].resolve_one(
            identity, reference_value
        )
    else:
        fallback_resolver = copy.copy(entity_resolvers["fallback"])
        fallback_resolver.reference_type = reference_type
        # TODO log warning
        resolved = fallback_resolver.resolve_one(identity, reference_value)

    # use cache to avoid multiple resolve for the same reference within one request
    # the runtime error is risen when we are outside the request context - in this case we just skip the cache
    with contextlib.suppress(RuntimeError):
        request.current_oarepo_requests_ui_resolve_cache[
            (reference_type, reference_value)
        ] = resolved

    return resolved


def fallback_label_result(reference: dict[str, str]) -> str:
    """Get a fallback label for a reference if there is no other way to get it."""
    id_ = list(reference.values())[0]
    return f"id: {id_}"


def fallback_result(reference: dict[str, str], **kwargs: Any) -> UIResolvedReference:
    """Get a fallback result for a reference if there is no other way to get it."""
    return {
        "reference": reference,
        "type": next(iter(reference.keys())),
        "label": fallback_label_result(reference),
        "links": {},
    }


class OARepoUIResolver(abc.ABC):
    """Base class for entity reference UI resolvers."""

    def __init__(self, reference_type: str) -> None:
        """Initialize the resolver.

        :param reference_type:  type of the reference (the key in the reference dict)
        """
        self.reference_type = reference_type

    @abc.abstractmethod
    def _get_id(self, entity: dict) -> str:
        """Get the id of the serialized entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found. Each entity must be API serialized to dict.
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        :return:            API serialization of the data of the entity or
                            None if the entity no longer exists

        Note: this call must return None if the entity does not exist,
        not raise an exception!
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved and API serialized entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def resolve_one(
        self, identity: Identity, _id: str, **kwargs: Any
    ) -> UIResolvedReference:
        """Resolve a single reference to a UI representation.

        :param identity:    identity of the user
        :param _id:         id of the entity
        :return:            UI representation of the reference
        """
        reference = {self.reference_type: _id}
        entity = self._search_one(identity, _id)
        if not entity:
            return fallback_result(reference, **kwargs)
        resolved = self._get_entity_ui_representation(entity, reference)
        return resolved

    def resolve_many(
        self, identity: Identity, ids: list[str]
    ) -> list[UIResolvedReference]:
        """Resolve many references to UI representations.

        :param identity:    identity of the user
        :param ids:         ids of the records of the type self.reference_type
        :return:            list of UI representations of the references
        """
        search_results = self._search_many(identity, ids)
        ret = []
        result: dict
        for result in search_results:
            # it would be simple if there was a map of results, can opensearch do this?
            ret.append(
                self._get_entity_ui_representation(
                    result, {self.reference_type: self._get_id(result)}
                )
            )
        return ret

    def _extract_links_from_resolved_reference(
        self, resolved_reference: dict
    ) -> dict[str, str]:
        """Extract links from a entity."""
        entity_links = {}
        if "links" in resolved_reference:
            entity_links = resolved_reference["links"]
        return entity_links


class GroupEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for group entity references."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        result = []
        for group_id in ids:
            try:
                group: RecordItem = current_groups_service.read(identity, group_id)
                result.append(group.data)
            except PermissionDeniedError:
                pass
        return result

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        try:
            group: RecordItem = current_groups_service.read(identity, _id)
            return group.data
        except PermissionDeniedError:
            return None

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        label = entity["name"]
        return UIResolvedReference(
            reference=reference,
            type="group",
            label=label,
            links=self._extract_links_from_resolved_reference(entity),
        )


class UserEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for user entity references."""

    @override
    def _get_id(self, result: RecordItem) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        result: list[dict] = []
        for user_id in ids:
            try:
                user: RecordItem = current_users_service.read(identity, user_id)
                result.append(user.data)
            except PermissionDeniedError:
                pass
        return result

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        try:
            user = current_users_service.read(identity, _id)
            return user.data
        except PermissionDeniedError:
            return None

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if entity["id"] == "system":
            label = _("System user")
        elif (
            "profile" in entity
            and "full_name" in entity["profile"]
            and entity["profile"]["full_name"]
        ):
            label = entity["profile"]["full_name"]
        elif "username" in entity and entity["username"]:
            label = entity["username"]
        else:
            label = fallback_label_result(reference)
        ret = UIResolvedReference(
            reference=reference,
            type="user",
            label=label,
            links=self._extract_links_from_resolved_reference(entity),
        )
        return ret


class RecordEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for entity entity references."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not ids:
            return []
        # todo what if search not permitted?
        service = get_matching_service_for_refdict({self.reference_type: list(ids)[0]})
        if not service:
            raise ValueError(
                f"No service found for handling reference type {self.reference_type}"
            )
        extra_filter = dsl.Q("terms", **{"id": list(ids)})
        return service.search(identity, extra_filter=extra_filter).to_dict()["hits"][
            "hits"
        ]

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        service = get_matching_service_for_refdict({self.reference_type: _id})
        if not service:
            raise ValueError(
                f"No service found for handling reference type {self.reference_type}"
            )
        try:
            return service.read(identity, _id, include_deleted=True).data
        except RecordDeletedException as e:
            return e.record

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if "metadata" in entity and "title" in entity["metadata"]:
            label = entity["metadata"]["title"]
        else:
            label = fallback_label_result(reference)
        ret = UIResolvedReference(
            reference=reference,
            type=list(reference.keys())[0],
            label=label,
            links=self._extract_links_from_resolved_reference(entity),
        )
        return ret


class RecordEntityDraftReferenceUIResolver(RecordEntityReferenceUIResolver):
    """UI resolver for entity entity draft references."""

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not ids:
            return []

        service: DraftsService = get_matching_service_for_refdict(
            {self.reference_type: list(ids)[0]}
        )
        extra_filter = dsl.Q("terms", **{"id": list(ids)})
        return service.search_drafts(identity, extra_filter=extra_filter).to_dict()[
            "hits"
        ]["hits"]

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        service: DraftsService = get_matching_service_for_refdict(
            {self.reference_type: _id}
        )
        return service.read_draft(identity, _id).data


class FallbackEntityReferenceUIResolver(OARepoUIResolver):
    """Fallback UI resolver if no other resolver is found."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        raise NotImplementedError("Intentionally not implemented")

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        reference = {self.reference_type: _id}
        try:
            service = get_matching_service_for_refdict(reference)
        except:  # noqa - we don't care which exception has been caught, just returning fallback result
            return cast(dict, fallback_result(reference))

        if not service:
            return cast(dict, fallback_result(reference))

        try:
            if self.reference_type.endswith("_draft"):
                response = service.read_draft(identity, _id)  # type: ignore
            else:
                response = service.read(identity, _id)
        except:  # noqa - we don't care which exception has been caught, just returning fallback result
            return cast(dict, fallback_result(reference))

        # TODO: should not this be "to_dict" ?
        if hasattr(response, "data"):
            response = response.data
        return response

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if "metadata" in entity and "title" in entity["metadata"]:
            label = entity["metadata"]["title"]
        else:
            label = fallback_label_result(reference)

        return UIResolvedReference(
            reference=reference,
            type=list(reference.keys())[0],
            label=label,
            links=self._extract_links_from_resolved_reference(entity),
        )


class KeywordUIEntityResolver(OARepoUIResolver):
    """UI resolver for keyword-like entities."""

    keyword = None

    @override
    def _get_id(self, entity: dict) -> str:
        """Get the id of the serialized entity.

        :result:    value of the keyword of the entity
        """
        return list(entity.values())[0]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Return list of references of keyword entities.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        return [{self.keyword: _id} for _id in ids]

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Return keyword entity reference.

        :param identity:    identity of the user
        :param _id:         the keyword value
        :return:            API serialization of the data
        """
        return {self.keyword: _id}


class AutoApproveUIEntityResolver(KeywordUIEntityResolver):
    """UI resolver for auto approve entities."""

    keyword = "auto_approve"

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of an auto approve entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        return UIResolvedReference(
            reference=reference,
            type=self.keyword,
            label=_("Auto approve"),
            links={},
        )
