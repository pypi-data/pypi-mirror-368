#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Validation of event types."""

from __future__ import annotations


def _serialized_topic_validator(value: str) -> str:
    """Validate the serialized topic. It must be a string with model and id separated by a single dot."""
    if len(value.split(".")) != 2:
        raise ValueError(
            "Serialized topic must be a string with model and id separated by a single dot."
        )
    return value
