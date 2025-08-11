from typing import List

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..db import CachedManager
from ..settings import saas_settings


class PermissionManager(CachedManager['Permission']):
    natural_key = ['name']

    def get_by_name(self, name: str):
        return self.get_from_cache_by_pk(name)

    def initialize_names(self, resources: List[str]):
        objs = []
        for resource in resources:
            for action in self.model.actions:
                name = saas_settings.PERMISSION_NAME_FORMATTER.format(resource=resource, action=action)
                objs.append(self.model(name=name, description=''))

        return self.bulk_create(objs, ignore_conflicts=True)


class Permission(models.Model):
    actions = ['read', 'write', 'admin']

    name = models.CharField(max_length=100, primary_key=True, editable=False)
    description = models.CharField(max_length=480, blank=True)
    # is this permission designed for internal use only?
    internal = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = PermissionManager()

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        db_table = 'saas_permission'
        ordering = ['name']

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)
