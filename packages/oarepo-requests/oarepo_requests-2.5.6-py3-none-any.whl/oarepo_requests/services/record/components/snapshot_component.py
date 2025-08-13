from invenio_records_resources.services.records.components import ServiceComponent
from opensearch_dsl.query import Bool, Term, Terms
from invenio_requests.proxies import current_requests_service
from invenio_access.permissions import system_identity
from invenio_requests.resolvers.registry import ResolverRegistry
from uuid import UUID
from flask import current_app


class RecordSnapshotComponent(ServiceComponent):

    def create_snapshot(self, record):
        topic_dict = ResolverRegistry.reference_entity(record)
        topic_type, topic_id = next(iter(topic_dict.items()))

        # find request for this record
        requests = list(current_requests_service.search(system_identity, extra_filter=Bool(
            must=[Term(**{f"topic.{topic_type}": topic_id}), Terms(type=current_app.config['PUBLISH_REQUEST_TYPES'])]),
                                                        sort='newest', size=1).hits)

        if requests:
            from oarepo_requests.snapshots import create_snapshot_and_possible_event
            create_snapshot_and_possible_event(record, record['metadata'], UUID(requests[0]['id']))

    def update(self, identity, *, record, **kwargs):
        """Update handler."""
        self.create_snapshot(record)

    def update_draft(self, identity, *, record, **kwargs):
        self.create_snapshot(record)
