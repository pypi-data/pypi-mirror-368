from typing import List, Any
from drf_spectacular.openapi import AutoSchema as _AutoSchema


__all__ = ['AutoSchema']


class AutoSchema(_AutoSchema):
    def get_filter_backends(self) -> List[Any]:
        return getattr(self.view, 'filter_backends', [])

    def get_description(self) -> str:
        description = super().get_description()

        permissions = []
        scopes = []
        for perm in self.view.permission_classes:
            if hasattr(perm, 'get_resource_permissions'):
                permissions = perm.get_resource_permissions(self.view, self.method)
            if hasattr(perm, 'get_resource_scopes'):
                scopes = perm.get_resource_scopes(self.view, self.method)

        if permissions:
            permissions_string = ' '.join([f'`{p}`' for p in permissions])
            description = f'**Permissions**: {permissions_string}\n\n{description}'
        if scopes:
            scopes_string = ' '.join([f'`{p}`' for p in scopes])
            description = f'**Scopes**: {scopes_string}\n\n{description}'
        return description
