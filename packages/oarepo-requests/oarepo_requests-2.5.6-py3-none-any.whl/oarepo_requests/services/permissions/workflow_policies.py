#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Permissions for requests based on workflows."""

from __future__ import annotations

from oarepo_workflows.requests.permissions import (
    CreatorsFromWorkflowRequestsPermissionPolicy,
)
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions

from oarepo_requests.services.permissions.generators.active import RequestActive


class RequestBasedWorkflowPermissions(DefaultWorkflowPermissions):
    """Base class for workflow permissions, subclass from it and put the result to Workflow constructor.

    This permission adds a special generator RequestActive() to the default permissions.
    Whenever the request is in `accept` action, the RequestActive generator matches.

    Example:
        class MyWorkflowPermissions(RequestBasedWorkflowPermissions):
            can_read = [AnyUser()]
    in invenio.cfg
    WORKFLOWS = {
        'default': Workflow(
            permission_policy_cls = MyWorkflowPermissions, ...
        )
    }

    """

    can_delete = DefaultWorkflowPermissions.can_delete + [RequestActive()]
    can_publish = [RequestActive()]
    can_edit = [RequestActive()]
    can_new_version = [RequestActive()]


__all__ = (
    "RequestBasedWorkflowPermissions",
    "CreatorsFromWorkflowRequestsPermissionPolicy",
)
