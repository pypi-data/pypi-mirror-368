from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .permission import Permission
from ..db import CachedManager


class RoleManager(CachedManager['Role']):
    def get_by_name(self, name: str):
        return self.get_from_cache_by_pk(name)


class Role(models.Model):
    """Pre-defined roles with permissions."""
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=480, blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    objects = RoleManager()

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        db_table = 'saas_role'
        ordering = ['created_at']

    def __str__(self):
        return self.name
