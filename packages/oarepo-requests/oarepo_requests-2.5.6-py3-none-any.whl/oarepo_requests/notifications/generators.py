from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING
from invenio_notifications.services.generators import EntityResolve, RecipientGenerator
from invenio_requests.proxies import current_requests
from invenio_requests.records.api import Request
from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_records.dictutils import dict_lookup
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service
from invenio_requests.proxies import current_events_service
from oarepo_requests.proxies import current_notification_recipients_resolvers_registry

log = logging.getLogger("oarepo_requests.notifications.generators")

if TYPE_CHECKING:
    from typing import Any

    from invenio_notifications.models import Notification


def _extract_entity_email_data(entity: Any) -> dict[str, Any]:
    def _get(entity, key):
        if isinstance(entity, dict) and key in entity:
            return entity.get(key, None)
        else:
            return getattr(entity, key, None)

    def _add(entity, key, res, transform=lambda x: x):
        v = _get(entity, key)
        if v:
            res[key] = transform(v)
            return v
        return None

    ret = {}
    email = _add(entity, "email", ret)
    if not email:
        log.error(
            "Entity %s %s does not have email/emails attribute, skipping.",
            type(entity),
            entity,
        )
        return {}
    _add(entity, "preferences", ret, transform=lambda x: dict(x))
    _add(entity, "id", ret)

    return ret


class EntityRecipient(RecipientGenerator):
    """Recipient generator working as handler for generic entity."""

    def __init__(self, key: str):
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient], backend_ids: list[str] = None):
        """"""
        backend_ids = notification.context["backend_ids"] if not backend_ids else backend_ids
        entity_ref_or_entity = dict_lookup(notification.context, self.key)

        if len(entity_ref_or_entity) != 1:
            # a hack - we need to have the original entity reference, not the resolved one
            entity_ref_or_entity = self._get_unresolved_entity_from_resolved(
                notification.context, self.key
            )
        if not entity_ref_or_entity:
            return

        entity_type = list(entity_ref_or_entity.keys())[0]

        for backend_id in backend_ids:
            generator_cls = current_notification_recipients_resolvers_registry.get(
                entity_type, {}
            ).get(backend_id)
            if generator_cls:
                generator = generator_cls(entity_ref_or_entity)
                generator(notification, recipients)

    def _get_unresolved_entity_from_resolved(self, context, key):
        """Get the unresolved entity from the resolved one."""
        match key.split(".", maxsplit=1):
            case "request", field:
                req = Request.get_record(context["request"]["id"])
                field_value = getattr(req, field)
                if field_value is not None:
                    return field_value.reference_dict
                return None
            case _:
                raise NotImplementedError(f"Can not resolve entity from key: {key}")


class SpecificEntityRecipient(RecipientGenerator):
    """Superclass for implementations of recipient generators for specific entities."""

    def __init__(self, key):
        self.key = key  # todo this is entity_reference, not path to entity as EntityRecipient, might be confusing

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients

    @abstractmethod
    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        raise NotImplementedError()

    def _resolve_entity(self) -> Any:
        entity_type = list(self.key)[0]
        registry = current_requests.entity_resolvers_registry

        registered_resolvers = registry._registered_types
        resolver = registered_resolvers.get(entity_type)
        proxy = resolver.get_entity_proxy(self.key)
        entity = proxy.resolve()
        return entity


class UserEmailRecipient(SpecificEntityRecipient):
    """User email recipient generator for a notification."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get user email of the entity."""
        # might be a system identity or a ghost user
        email = getattr(entity, "email", None)
        if email:
            return {email: Recipient(data=_extract_entity_email_data(entity))}
        else:
            return {}


class GroupEmailRecipient(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data=_extract_entity_email_data(user))
            for user in entity.users.all()
            if getattr(user, "email", None)
        }


class MultipleRecipientsEmailRecipients(SpecificEntityRecipient):
    """Recipient generator returning emails of entity with multiple recipients."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get recipient emails of entity with multiple recipients.."""
        final_recipients = {}
        for current_entity in entity.entities:
            recipient_entity = current_entity.resolve()
            if hasattr(recipient_entity, "email"):
                final_recipients[recipient_entity.email] = Recipient(
                    data=_extract_entity_email_data(recipient_entity)
                )
            elif hasattr(recipient_entity, "emails"):
                for email_data in recipient_entity.emails:
                    final_recipients[email_data["email"]] = Recipient(
                        _extract_entity_email_data(email_data)
                    )
            else:
                log.error(
                    "Entity %s %s does not have email/emails attribute, skipping.",
                    type(recipient_entity),
                    recipient_entity,
                )
                continue
        return final_recipients

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Get the emails from the multiple recipients entity."""
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients


class RequestEntityResolve(EntityResolve):
    """Entity resolver that adds the correct title if it is missing."""

    def __call__(self, notification):
        notification = super().__call__(notification)
        request_dict = notification.context["request"]
        if request_dict.get("title"):
            return request_dict

        request = Request.get_record(request_dict["id"])
        if hasattr(request.type, "stateful_name"):
            # If the request type has a stateful name, use it
            # note: do not have better identity here, so using system_identity
            # as a fallback
            request_dict["title"] = request.type.stateful_name(
                system_identity, topic=None
            )
        return notification

class OARepoRequestParticipantsRecipient(RecipientGenerator):
    """Recipient generator based on request and it's events."""

    def __init__(self, key: str):
        """Ctor."""
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Fetch users involved in request and add as recipients."""
        request = dict_lookup(notification.context, self.key)


        # hack for invenio compatibility
        before_keys = set(recipients.keys())
        EntityRecipient("request.created_by")(notification, recipients, backend_ids=["email"])
        EntityRecipient("request.receiver")(notification, recipients, backend_ids=["email"])
        # can't replace the dict due to invenio pattern
        for id_ in set(recipients.keys()) - before_keys:
            recipients[str(recipients[id_].data["id"])] = recipients[id_]
            del recipients[id_]

        # assume events can only be done by users
        # fetching all request events to get involved users
        request_events = current_events_service.scan(
            identity=system_identity,
            extra_filter=dsl.Q("term", request_id=request["id"]),
        )
        # assume commenters can only be users
        user_ids =             {
                re["created_by"]["user"]
                for re in request_events
                if re["created_by"].get("user")
            }

        filter_ = dsl.Q("terms", **{"id": list(user_ids)})
        users = current_users_service.scan(system_identity, extra_filter=filter_)
        for u in users:
            recipients[u["id"]] = Recipient(data=u)

        return recipients
