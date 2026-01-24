from django.urls import path

from .views import ChatAPIView, HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("chat/", ChatAPIView.as_view(), name="api-chat"),
]
