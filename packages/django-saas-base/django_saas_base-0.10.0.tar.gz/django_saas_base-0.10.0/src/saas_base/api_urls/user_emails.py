from django.urls import path
from ..endpoints.user_emails import (
    UserEmailListEndpoint,
    UserEmailItemEndpoint,
    AddUserEmailRequestEndpoint,
    AddUserEmailConfirmEndpoint,
)

urlpatterns = [
    path('', UserEmailListEndpoint.as_view()),
    path('add/request/', AddUserEmailRequestEndpoint.as_view()),
    path('add/confirm/', AddUserEmailConfirmEndpoint.as_view()),
    path('<pk>/', UserEmailItemEndpoint.as_view()),
]
