#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the UI resources."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

import marshmallow as ma
from flask import current_app
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_request_type_registry
from oarepo_runtime.services.custom_fields import CustomFields, InlinedCustomFields
from oarepo_ui.resources.components import AllowedHtmlTagsComponent
from oarepo_ui.resources.config import FormConfigResourceConfig, UIResourceConfig
from oarepo_ui.resources.links import UIRecordLink

from oarepo_requests.ui.components import (
    ActionLabelsComponent,
    FormConfigCustomFieldsComponent,
    FormConfigRequestTypePropertiesComponent,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_resources.serializers.base import BaseSerializer
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.request_types import RequestType


def _get_custom_fields_ui_config(key: str, **kwargs: Any) -> list[dict]:
    return current_app.config.get(f"{key}_UI", [])


class RequestTypeSchema(ma.fields.Str):
    """Schema that makes sure that the request type is a valid request type."""

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> RequestType:
        """Deserialize the value and check if it is a valid request type."""
        ret = super()._deserialize(value, attr, data, **kwargs)
        return current_request_type_registry.lookup(ret, quiet=True)


class RequestsFormConfigResourceConfig(FormConfigResourceConfig):
    """Config for the requests form config resource."""

    url_prefix = "/requests"
    blueprint_name = "oarepo_requests_form_config"
    components = [
        AllowedHtmlTagsComponent,
        FormConfigCustomFieldsComponent,
        FormConfigRequestTypePropertiesComponent,
        ActionLabelsComponent,
    ]
    request_view_args = {"request_type": RequestTypeSchema()}
    routes = {
        "form_config": "/configs/<request_type>",
    }


class RequestUIResourceConfig(UIResourceConfig):
    """Config for request detail page."""

    url_prefix = "/requests"
    api_service = "requests"
    blueprint_name = "oarepo_requests_ui"
    template_folder = "templates"
    templates = {
        "detail": "RequestDetail",
    }
    routes = {
        "detail": "/<pid_value>",
    }
    ui_serializer_class = "oarepo_requests.resources.ui.OARepoRequestsUIJSONSerializer"
    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}/{id}"),
    }
    components = [AllowedHtmlTagsComponent]

    error_handlers = {
        PIDDeletedError: "tombstone",
        PIDDoesNotExistError: "not_found",
        PIDUnregistered: "not_found",
        KeyError: "not_found",
        PermissionDeniedError: "permission_denied",
    }

    request_view_args = {"pid_value": ma.fields.Str()}

    @property
    def ui_serializer(self) -> BaseSerializer:
        """Return the UI serializer for the request."""
        return obj_or_import_string(self.ui_serializer_class)()

    def custom_fields(self, **kwargs: Any) -> dict:
        """Get the custom fields for the request."""
        api_service = current_service_registry.get(self.api_service)

        ui: list[dict] = []
        ret = {
            "ui": ui,
        }

        # get the record class
        if not hasattr(api_service, "record_cls"):
            return ret
        record_class: type[Record] = api_service.record_cls
        if not record_class:
            return ret
        # try to get custom fields from the record
        for _fld_name, fld in sorted(inspect.getmembers(record_class)):
            if isinstance(fld, InlinedCustomFields):
                prefix = ""
            elif isinstance(fld, CustomFields):
                prefix = fld.key + "."
            else:
                continue

            ui_config = _get_custom_fields_ui_config(fld.config_key, **kwargs)
            if not ui_config:
                continue

            for section in ui_config:
                ui.append(
                    {
                        **section,
                        "fields": [
                            {
                                **field,
                                "field": prefix + field["field"],
                            }
                            for field in section.get("fields", [])
                        ],
                    }
                )
        return ret
