#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration for the oarepo request service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from invenio_records_resources.services.base.links import Link
from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink

from oarepo_requests.resolvers.interface import resolve_entity

if TYPE_CHECKING:
    from invenio_requests.records.api import Request
log = logging.getLogger(__name__)


class RequestEntityLinks(Link):
    """Utility class for keeping track of and resolve links."""

    def __init__(self, entity: str, when: callable = None):
        """Constructor."""
        self._entity = entity
        self._when_func = when

    def expand(self, obj: Request, context: dict) -> dict:
        """Create the request links."""
        res = {}
        resolved = resolve_entity(self._entity, obj, context)
        if "links" in resolved:
            res.update(resolved["links"])

        return res


class RedirectLink(Link):
    def __init__(self, when: callable = None):
        """Constructor."""
        self._when_func = when

    def expand(self, obj: Request, context: dict) -> dict:
        """Create the request links."""
        link = None
        if hasattr(obj.type, "get_ui_redirect_url"):
            link = getattr(obj.type, "get_ui_redirect_url")(obj, context)
        return link


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    service_id = "oarepo_requests"

    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
        "self_html": RequestLink("{+ui}/requests/{id}"),
        "topic": RequestEntityLinks(entity="topic"),
        "created_by": RequestEntityLinks(entity="created_by"),
        "receiver": RequestEntityLinks(entity="receiver"),
        "ui_redirect_url": RedirectLink(),
    }
