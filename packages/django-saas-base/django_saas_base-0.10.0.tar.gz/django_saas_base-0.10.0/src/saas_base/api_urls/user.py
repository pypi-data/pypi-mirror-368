from django.urls import path
from ..endpoints.user import (
    UserEndpoint,
    UserPasswordEndpoint,
)

urlpatterns = [
    path('', UserEndpoint.as_view()),
    path('password/', UserPasswordEndpoint.as_view()),
]
