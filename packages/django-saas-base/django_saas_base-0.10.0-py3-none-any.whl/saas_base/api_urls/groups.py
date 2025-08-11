from django.urls import path
from ..endpoints.groups import (
    GroupListEndpoint,
    GroupItemEndpoint,
)

urlpatterns = [
    path('', GroupListEndpoint.as_view()),
    path('<pk>/', GroupItemEndpoint.as_view()),
]
