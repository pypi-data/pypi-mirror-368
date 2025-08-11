from saas_base.models import Group, Permission
from saas_base.test import SaasTestCase


class TestAccountScopes(SaasTestCase):
    user_id = SaasTestCase.GUEST_USER_ID

    @classmethod
    def setUpTestData(cls):
        Permission.objects.initialize_names(['account'])

    def test_none_user_permissions(self):
        member = self.get_user_member()
        self.assertEqual(member.user_permissions, [])

    def test_exist_user_permissions(self):
        self.add_user_perms('account.read', 'account.write', 'account.admin')
        member = self.get_user_member()
        scopes = set(member.user_permissions)
        self.assertEqual(scopes, {'account.read', 'account.write', 'account.admin'})

    def test_none_role_permissions(self):
        member = self.get_user_member()
        self.assertEqual(member.role_permissions, [])

    def test_exist_role_permissions(self):
        member = self.get_user_member()
        member.role_id = 'admin'
        member.save()
        self.assertEqual(set(member.role_permissions), {'tenant.admin', 'tenant.read', 'tenant.write'})

    def test_none_group_permissions(self):
        member = self.get_user_member()
        self.assertEqual(member.group_permissions, [])

    def test_exist_group_permissions(self):
        group = Group.objects.create(tenant=self.tenant, name='Group')
        perms = [item for item in Permission.objects.all() if item.name.startswith('account.')]
        group.permissions.add(*perms)

        member = self.get_user_member()
        member.groups.add(group)
        scopes = set(member.group_permissions)
        self.assertEqual(scopes, {'account.read', 'account.write', 'account.admin'})
