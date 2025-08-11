from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as BaseModelBackend
from saas_base.models import UserEmail

__all__ = ['ModelBackend']

UserModel = get_user_model()


class ModelBackend(BaseModelBackend):
    @staticmethod
    def _get_user_by_username(username: str):
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            if '@' not in username:
                return None
            try:
                obj = UserEmail.objects.select_related('user').get(email=username)
                if obj.verified and obj.primary:
                    return obj.user
            except UserEmail.DoesNotExist:
                return None
        return None

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return

        user = self._get_user_by_username(username)
        if user is None:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        elif user.check_password(password) and self.user_can_authenticate(user):
            return user
