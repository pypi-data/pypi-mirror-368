from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)

class RDMPIDServiceResultResolver(ServiceResultResolver):
    """Service result resolver for draft records."""

    def _reference_entity(self, entity):
        """Create a reference dict for the given result item."""
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}

class DraftServiceResultResolver(RDMPIDServiceResultResolver):
    """Service result resolver for draft records."""

    @property
    def draft_cls(self):
        """Get specified draft class or from service."""
        return self.get_service().draft_cls

    def matches_entity(self, entity):
        """Check if the entity is a draft."""
        if isinstance(entity, self.draft_cls):
            return True

        return super().matches_entity(entity=entity)
