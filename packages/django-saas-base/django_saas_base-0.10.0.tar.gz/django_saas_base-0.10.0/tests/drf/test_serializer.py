from saas_base.test import SaasTestCase
from saas_base.drf.serializers import ModelSerializer
from saas_base.models import Member
from saas_base.serializers.user import SimpleUserSerializer


class MemberSerializer(ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = '__all__'
        flatten_fields = ['user']


class TestModelSerializer(SaasTestCase):
    user_id = SaasTestCase.GUEST_USER_ID

    def test_flatten_fields(self):
        user = self.get_user()
        user.first_name = 'Django'
        user.save()
        member = self.get_user_member()
        serializer = MemberSerializer(member)
        self.assertEqual(serializer.data['user_name'], 'Django')
