from django.urls import path
from .views import (
    view_signup_code,
    view_reset_password,
    view_invite_member,
)


urlpatterns = [
    path('signup_code.<suffix>', view_signup_code),
    path('reset_password.<suffix>', view_reset_password),
    path('invite_member.<suffix>', view_invite_member),
]
