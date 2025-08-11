from django.urls import path
from ..endpoints.user_members import (
    UserMemberListEndpoint,
    UserMemberItemEndpoint,
)

urlpatterns = [
    path('', UserMemberListEndpoint.as_view()),
    path('<pk>/', UserMemberItemEndpoint.as_view()),
]
