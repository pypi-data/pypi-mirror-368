#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Classes that define allowed reference types for the topic and receiver references."""

from __future__ import annotations

from typing import Self

from invenio_records_resources.references import RecordResolver
from invenio_requests.proxies import current_requests

from oarepo_requests.proxies import current_oarepo_requests


class ModelRefTypes:
    """This class is used to define the allowed reference types for the topic reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_TOPICS).
    """

    def __init__(self, published: bool = False, draft: bool = False) -> None:
        """Initialize the class."""
        self.published = published
        self.draft = draft

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        ret = []
        for ref_type in current_requests.entity_resolvers_registry:
            if not isinstance(ref_type, RecordResolver):
                continue
            is_draft: bool = getattr(ref_type.record_cls, "is_draft", False)
            if self.published and not is_draft or self.draft and is_draft:
                ret.append(ref_type.type_key)
        return ret


class ReceiverRefTypes:
    """This class is used to define the allowed reference types for the receiver reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_RECEIVERS).
    """

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        return current_oarepo_requests.allowed_receiver_ref_types
