import typing as t
from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS


DEFAULT_PERMISSIONS = [
    ('tenant.read', 'Read permission for tenants'),
    ('tenant.write', 'Write permission for tenants'),
    ('tenant.admin', 'Admin permission for tenants'),
]


def create_permissions_receiver(permissions: t.List[t.Tuple[str, str]]):
    def _create_permissions(app_config, verbosity=2, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
        if not app_config.models_module:
            return

        if app_config.label != 'saas_base':
            return

        try:
            Permission = apps.get_model(app_config.label, 'Permission')
        except LookupError:
            return

        existed_perms = set(Permission.objects.values_list('name', flat=True).all())

        to_add_perms = []
        for name, description in permissions:
            if name not in existed_perms:
                to_add_perms.append(Permission(name=name, description=description))

        if to_add_perms:
            Permission.objects.using(using).bulk_create(to_add_perms, ignore_conflicts=True)
        if verbosity >= 2:
            for perm in to_add_perms:
                print(f"Adding saas_base.Permission '{perm.name}'")

    return _create_permissions


create_permissions = create_permissions_receiver(DEFAULT_PERMISSIONS)
