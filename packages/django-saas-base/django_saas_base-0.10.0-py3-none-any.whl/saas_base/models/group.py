import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .permission import Permission


class Group(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    tenant = models.ForeignKey(settings.SAAS_TENANT_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    managed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        unique_together = [['tenant', 'name']]
        db_table = 'saas_group'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)
