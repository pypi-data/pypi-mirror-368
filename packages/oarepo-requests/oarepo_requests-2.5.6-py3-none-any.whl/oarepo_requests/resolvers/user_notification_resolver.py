from invenio_access.permissions import system_identity, system_user_id
from invenio_users_resources.entity_resolvers import UserProxy, UserResolver
from invenio_users_resources.proxies import current_users_service


class UserNotificationProxy(UserProxy):
    def _resolve(self):
        """Resolve the User from the proxy's reference dict, or system_identity."""
        user_id = self._parse_ref_dict_id()
        if user_id == system_user_id:  # system_user_id is a string: "system"
            return self.system_record()
        else:
            try:
                return current_users_service.read(system_identity, user_id).data
            except:
                return self.ghost_record({"id": user_id})


class UserNotificationResolver(UserResolver):
    def _get_entity_proxy(self, ref_dict):
        """Return a UserProxy for the given reference dict."""
        return UserNotificationProxy(self, ref_dict)
