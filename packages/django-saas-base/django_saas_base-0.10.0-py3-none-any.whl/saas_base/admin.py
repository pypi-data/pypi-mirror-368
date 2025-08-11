from django.contrib import admin
from .models import (
    Permission,
    Role,
    Group,
    Member,
    UserEmail,
    Tenant,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'internal', 'created_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'owner', 'expires_at', 'created_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'tenant', 'name', 'managed', 'created_at']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'tenant', 'user', 'name', 'email', 'is_staff', 'status', 'created_at']


@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'primary', 'verified', 'created_at']
