#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Serializers for the UI schema."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any, cast

from flask import g
from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.services.errors import RecordPermissionDeniedError
from invenio_pidstore.errors import PIDDeletedError
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from ..proxies import current_oarepo_requests
from ..resolvers.ui import resolve
from ..services.ui_schema import (
    UIBaseRequestEventSchema,
    UIBaseRequestSchema,
    UIRequestTypeSchema,
)
from ..utils import reference_to_tuple

if TYPE_CHECKING:
    from flask_principal import Identity


def _reference_map_from_list(obj_list: list[dict]) -> dict[str, set]:
    """Create a map of references from a list of requests from opensearch.

    For each of the serialized requests in the list, extract the fields that represent
    references to other entities and create a map of entity type to a set of identifiers.

    The fields are determined by the REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS config key.
    """
    if not obj_list:
        return {}
    reference_map = defaultdict(set)
    reference_types = current_oarepo_requests.ui_serialization_referenced_fields
    for hit in obj_list:
        for reference_type in reference_types:
            if reference_type in hit:
                reference = hit[reference_type]
                if reference:
                    reference_map[list(reference.keys())[0]].add(
                        list(reference.values())[0]
                    )
    return reference_map


def _create_cache(
    identity: Identity, reference_map: dict[str, set[str]]
) -> dict[tuple[str, str], dict]:
    """Create a cache of resolved references.

    For each of the (entity_type, entity_ids) pairs in the reference_map, resolve the references
    using the entity resolvers and create a cache of the resolved references.

    This call uses resolve_many to extract all references of the same type.
    """
    cache: dict[tuple[str, str], dict] = {}
    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers
    for reference_type, values in reference_map.items():
        if reference_type in entity_resolvers:
            resolver = entity_resolvers[reference_type]
            results = resolver.resolve_many(identity, list(values))
            # we are expecting "reference" in results
            cache_for_type = {
                reference_to_tuple(result["reference"]): cast(dict, result)
                for result in results
            }
            cache |= cache_for_type
    return cache


class CachedReferenceResolver:
    """Cached reference resolver."""

    def __init__(self, identity: Identity, serialized_requests: list[dict]) -> None:
        """Initialise the resolver.

        The references is a dictionary of requests in opensearch list format
        """
        reference_map = _reference_map_from_list(serialized_requests)
        self._cache = _create_cache(identity, reference_map)
        self._identity = identity

    def dereference(self, reference: dict, **context: Any) -> dict:
        """Dereference a reference.

        If the reference is in the cache, return the cached value.
        Otherwise, resolve the reference and return the resolved value.

        The resolved value has a "reference" key and the rest is the
        dereferenced dict given from ui entity resolver.

        :param reference:   reference to resolve
        :param context:     additional context
        """
        key = reference_to_tuple(reference)
        if key in self._cache:
            return self._cache[key]
        else:
            try:
                return cast(dict, resolve(self._identity, reference))
            except PIDDeletedError:
                return {"reference": reference, "status": "deleted"}
            except RecordPermissionDeniedError:
                return {"reference": reference, "status": "denied"}


class OARepoRequestsUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer."""

    def __init__(self) -> None:
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIBaseRequestSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )

    def dump_obj(self, obj: Any, *args: Any, **kwargs: Any) -> dict:
        """Dump a single object.

        Do not create a cache for single objects as there is no performance boost by doing so.
        """
        extra_context = {
            "resolved": CachedReferenceResolver(self.schema_context["identity"], [])
        }
        return super().dump_obj(obj, *args, extra_context=extra_context, **kwargs)

    def dump_list(self, obj_list: dict, *args: Any, **kwargs: Any) -> list[dict]:
        """Dump a list of objects.

        This call at first creates a cache of resolved references which is used later on
        to serialize them.

        :param obj_list:    objects to serialize in opensearch list format
        """
        extra_context = {
            "resolved": CachedReferenceResolver(
                self.schema_context["identity"], obj_list["hits"]["hits"]
            )
        }
        return super().dump_list(obj_list, *args, extra_context=extra_context, **kwargs)


class OARepoRequestEventsUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer for request events."""

    def __init__(self) -> None:
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIBaseRequestEventSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )


class OARepoRequestTypesUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer for request types."""

    def __init__(self) -> None:
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIRequestTypeSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )

    def dump_obj(self, obj: Any, *args: Any, **kwargs: Any) -> dict:
        """Dump a single object."""
        extra_context = {"topic": obj.topic} if hasattr(obj, "topic") else {}
        return super().dump_obj(obj, *args, extra_context=extra_context, **kwargs)

    def dump_list(self, obj_list: dict, *args: Any, **kwargs: Any) -> list[dict]:
        """Dump a list of objects."""
        return super().dump_list(
            obj_list,
            *args,
            extra_context={"topic": getattr(obj_list, "topic", None)},
            **kwargs,
        )
