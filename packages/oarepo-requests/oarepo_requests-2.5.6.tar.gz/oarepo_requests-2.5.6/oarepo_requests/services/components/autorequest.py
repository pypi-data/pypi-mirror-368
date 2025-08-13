from __future__ import annotations
from invenio_records_resources.services.records.components import ServiceComponent
from typing import TYPE_CHECKING
from oarepo_requests.services.permissions.requester import create_autorequests

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record


class AutorequestComponent(ServiceComponent):
    """Component for assigning request numbers to new requests."""

    def create(self, identity: Identity, data: dict=None, record: Record=None, **kwargs)->None:
        """Create requests that should be created automatically on state change.

        For each of the WorkflowRequest definition in the workflow of the record,
        take the needs from the generators of possible creators. If any of those
        needs is an auto_request_need, create a request for it automatically.
        """
        create_autorequests(identity, record, self.uow, **kwargs)