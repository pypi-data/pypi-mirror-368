from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from invenio_pidstore.errors import PersistentIdentifierError

from oarepo_requests.resolvers.ui import resolve

if TYPE_CHECKING:
    from invenio_requests.records import Request
log = logging.getLogger(__name__)


# todo consider - we are not using this strictly in the ui context - so how should we separate these things in the future
def resolve_entity(entity: str, obj: Request, ctx: dict[str, Any]) -> dict:
    """Resolve the entity and put it into the context cache.

    :param obj: Request object
    :param ctx: Context cache
    :return: The resolved entity
    """
    entity_field_value = getattr(obj, entity)
    if not entity_field_value:
        return {}

    reference_dict: dict = entity_field_value.reference_dict

    key = entity_context_key(reference_dict)
    if key in ctx:
        return ctx[key]
    try:
        entity = resolve(ctx["identity"], reference_dict)
    except Exception as e:  # noqa
        if not isinstance(e, PersistentIdentifierError):
            log.exception(
                "Error resolving %s for identity %s",
                reference_dict,
                ctx["identity"],
            )
        entity = {"links": {}}
    ctx[key] = entity
    return entity


def entity_context_key(reference_dict: dict) -> str:
    """Create a key for the entity context cache."""
    return "entity:" + ":".join(
        f"{x[0]}:{x[1]}" for x in sorted(reference_dict.items())
    )
