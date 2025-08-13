#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Generator is triggered when workflow action is being performed."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_records_permissions.generators import Generator
from opensearch_dsl.query import Query

from oarepo_requests.services.permissions.identity import request_active

if TYPE_CHECKING:
    from flask_principal import Identity, Need


class RequestActive(Generator):
    """A generator that requires that a request is being handled.

    This is useful for example when a caller identity should have greater permissions
    when calling an action from within a request.
    """

    def needs(self, **context: Any) -> list[Need]:
        """Return the needs required for the action."""
        return [request_active]

    def query_filter(self, identity: Identity = None, **context: Any) -> Query:
        """Return the query filter for the action."""
        return Query("match_none")
