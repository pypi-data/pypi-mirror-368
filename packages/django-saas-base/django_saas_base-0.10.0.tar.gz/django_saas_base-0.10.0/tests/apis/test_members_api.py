from tests.client import FixturesTestCase
from saas_base.models import Member


class TestMembersAPI(FixturesTestCase):
    user_id = FixturesTestCase.GUEST_USER_ID

    def test_list_users_via_owner(self):
        self.force_login(self.OWNER_USER_ID)
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 200)

    def test_list_users_via_guest_user(self):
        self.force_login()
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 403)

        self.add_user_perms('tenant.read')
        resp = self.client.get('/m/members/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertNotIn('user', member)

    def test_list_include_user(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?include=user')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertIn('user', member)

    def test_list_include_permissions(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?include=permissions')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        member = data['results'][0]
        self.assertIn('permissions', member)

    def test_list_members_by_status(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?status=request')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 0)
        resp = self.client.get('/m/members/?status=active')
        data = resp.json()
        self.assertNotEqual(data['count'], 0)

    def test_list_members_by_staff(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        resp = self.client.get('/m/members/?is_staff=false')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 0)
        resp = self.client.get('/m/members/?is_staff=true')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertNotEqual(data['count'], 0)

    def test_invite_member_signup(self):
        self.add_user_perms('tenant.admin')
        self.force_login()
        data = {'name': 'Django'}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {'email': ['This field is required.']})

        # invite non-exist user
        data = {'email': 'signup@example.com'}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        member = resp.json()
        self.assertEqual(member['status'], 'request')

        # invite existing user
        user = self.get_user(self.STAFF_USER_ID)
        data = {'email': user.email}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        member = resp.json()
        self.assertEqual(member['status'], 'waiting')

    def test_invite_with_permissions(self):
        self.add_user_perms('tenant.admin')
        self.force_login()

        user = self.get_user(self.STAFF_USER_ID)
        data = {'email': user.email, 'permissions': ['tenant.read']}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        permissions = resp.json()['permissions']
        self.assertEqual(permissions[0]['name'], 'tenant.read')

    def test_invite_with_role(self):
        self.add_user_perms('tenant.admin')
        self.force_login()

        user = self.get_user(self.STAFF_USER_ID)
        data = {'email': user.email, 'role': 'admin'}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        permissions = [p['name'] for p in resp.json()['role']['permissions']]
        self.assertIn('tenant.read', permissions)

    def test_view_member_item(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.get(f'/m/members/{member.id}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('groups', data)
        self.assertIn('permissions', data)

    def test_update_member_item(self):
        self.add_user_perms('tenant.read')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        data = {'permissions': ['tenant.read']}
        resp = self.client.patch(f'/m/members/{member.id}/', data=data)
        self.assertEqual(resp.status_code, 403)
        self.add_user_perms('tenant.admin')
        resp = self.client.patch(f'/m/members/{member.id}/', data=data)
        self.assertEqual(resp.status_code, 200)
        permissions = resp.json()['permissions']
        result = [p['name'] for p in permissions]
        self.assertEqual(result, ['tenant.read'])

    def test_remove_member_item(self):
        self.add_user_perms('tenant.admin')
        self.force_login()
        member = Member.objects.filter(tenant=self.tenant, user_id=self.user_id).first()
        resp = self.client.delete(f'/m/members/{member.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_invite_duplicate_member(self):
        self.force_login(self.OWNER_USER_ID)
        email = 'demo-1@example.com'
        data = {'email': email, 'permissions': ['tenant.read']}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['email'], ['This user has already been invited.'])

    def test_already_invited(self):
        self.force_login(self.OWNER_USER_ID)
        member = Member.objects.filter(
            tenant_id=self.tenant_id,
            user_id=self.OWNER_USER_ID,
        ).first()
        member.email = 'demo-1@example.com'
        member.save()
        data = {'email': member.email, 'permissions': ['tenant.read']}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['email'], ['This email has already been invited.'])

    def test_invite_self(self):
        self.force_login(self.OWNER_USER_ID)
        # clean self member
        Member.objects.filter(
            tenant_id=self.tenant_id,
            user_id=self.OWNER_USER_ID,
        ).delete()
        email = 'demo-1@example.com'
        data = {'email': email, 'permissions': ['tenant.read']}
        resp = self.client.post('/m/members/', data=data)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'active')
