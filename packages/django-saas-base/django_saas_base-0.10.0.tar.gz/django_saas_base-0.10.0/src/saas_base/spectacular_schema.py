from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from drf_spectacular.extensions import OpenApiViewExtension


class AuthResponseSerializer(serializers.Serializer):
    next = serializers.CharField()


class FixedPasswordLogInEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.PasswordLogInEndpoint'

    def view_replacement(self):
        class PasswordLogInEndpoint(self.target_class):
            @extend_schema(summary='Log In', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return PasswordLogInEndpoint


class FixedLogoutEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.LogoutEndpoint'

    def view_replacement(self):
        class LogoutEndpoint(self.target_class):
            @extend_schema(summary='Log Out', request=None, responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return LogoutEndpoint


class FixedSignupConfirmEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.SignupConfirmEndpoint'

    def view_replacement(self):
        class SignupConfirmEndpoint(self.target_class):
            @extend_schema(summary='Sign Up', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return SignupConfirmEndpoint


class FixedSignupRequestEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.auth.SignupRequestEndpoint'

    def view_replacement(self):
        class SignupRequestEndpoint(self.target_class):
            @extend_schema(summary='Request to Sign-up', responses={204: None})
            def post(self, *args, **kwargs):
                pass

        return SignupRequestEndpoint


class FixedPasswordResetEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.password.PasswordResetEndpoint'

    def view_replacement(self):
        class PasswordResetEndpoint(self.target_class):
            @extend_schema(summary='Password Reset', responses={200: AuthResponseSerializer})
            def post(self, *args, **kwargs):
                pass

        return PasswordResetEndpoint


class FixedPasswordForgotEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.password.PasswordForgotEndpoint'

    def view_replacement(self):
        class PasswordForgotEndpoint(self.target_class):
            @extend_schema(summary='Password Forgot', responses={204: None})
            def post(self, *args, **kwargs):
                pass

        return PasswordForgotEndpoint


class FixedUserPasswordEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.user.UserPasswordEndpoint'

    def view_replacement(self):
        class UserPasswordEndpoint(self.target_class):
            @extend_schema(summary='Update Password')
            def post(self, *args, **kwargs):
                pass

        return UserPasswordEndpoint


class FixedUserEmailItemEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.user_emails.UserEmailItemEndpoint'

    def view_replacement(self):
        class UserEmailItemEndpoint(self.target_class):
            @extend_schema(summary='View Email Details')
            def get(self, *args, **kwargs):
                pass

        return UserEmailItemEndpoint


class FixedUserMemberListEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.user_members.UserMemberListEndpoint'

    def view_replacement(self):
        class UserMemberListEndpoint(self.target_class):
            @extend_schema(summary='List Memberships')
            def get(self, *args, **kwargs):
                pass

        return UserMemberListEndpoint


class FixedUserMemberItemEndpoint(OpenApiViewExtension):
    target_class = 'saas_base.endpoints.user_members.UserMemberItemEndpoint'

    def view_replacement(self):
        class UserMemberItemEndpoint(self.target_class):
            @extend_schema(summary='Show Membership')
            def get(self, *args, **kwargs):
                pass

            @extend_schema(summary='Update Membership')
            def patch(self, *args, **kwargs):
                pass

            @extend_schema(summary='Remove Membership')
            def delete(self, *args, **kwargs):
                pass

        return UserMemberItemEndpoint
