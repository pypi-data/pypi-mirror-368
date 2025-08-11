from django.urls import path
from ..endpoints.members import (
    MemberListEndpoint,
    MemberItemEndpoint,
)

urlpatterns = [
    path('', MemberListEndpoint.as_view()),
    path('<pk>/', MemberItemEndpoint.as_view()),
]
