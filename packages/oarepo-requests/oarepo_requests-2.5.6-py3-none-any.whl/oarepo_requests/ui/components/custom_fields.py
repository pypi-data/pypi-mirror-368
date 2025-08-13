#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request custom fields component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

from oarepo_requests.types.generic import OARepoRequestType

if TYPE_CHECKING:
    from invenio_requests.customizations import RequestType


class FormConfigCustomFieldsComponent(UIResourceComponent):
    """Component for adding custom fields to request's form config."""

    def form_config(
        self, *, view_args: dict[str, Any], form_config: dict, **kwargs: Any
    ) -> None:
        """Add custom fields to the form config."""
        type_ = view_args.get("request_type")
        # ignore the type as we are checking for alternatives below
        form: dict | list = getattr(type_, "form", None)  # type: ignore
        if not form:
            return

        if isinstance(form, dict):
            # it is just a single field
            form = [{"section": "", "fields": [form]}]
        elif isinstance(form, list):
            for it in form:
                if not isinstance(it, dict):
                    raise ValueError(f"Form section must be a dictionary: {it}")
                assert "section" in it, f"Form section must contain 'section' key: {it}"
                assert "fields" in it, f"Form section must contain 'fields' key: {it}"
                assert isinstance(
                    it["fields"], list
                ), f"Form section fields must be a list: {it}"
        else:
            raise ValueError(
                f"form must be either dict containing a definition of a single field or a list of sections: '{form}'. "
                f"See https://inveniordm.docs.cern.ch/customize/metadata/custom_fields/records/#upload-deposit-form "
                f"for details on the format."
            )

        form_config["custom_fields"] = {"ui": form}


class FormConfigRequestTypePropertiesComponent(UIResourceComponent):
    """Component for adding request type properties to request's form config."""

    def form_config(
        self, *, view_args: dict[str, Any], form_config: dict, **kwargs: Any
    ) -> None:
        """Add request type properties to the form config (dangerous, editable, has_form)."""
        type_: RequestType = view_args.get("request_type")

        request_type_properties = {}
        if type_ and isinstance(type_, OARepoRequestType):
            if hasattr(type_, "dangerous"):
                request_type_properties["dangerous"] = type_.dangerous
            if hasattr(type_, "is_editable"):
                request_type_properties["editable"] = type_.is_editable
            if hasattr(type_, "has_form"):
                request_type_properties["has_form"] = type_.has_form

        form_config["request_type_properties"] = request_type_properties
