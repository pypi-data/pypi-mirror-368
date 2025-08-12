from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(prefix="camera", viewset=views.CameraViewSet)
urlpatterns = [
    path("preview/", views.preview, name='preview'),
    path("history/", views.history, name='history'),
    path("playback/", views.playback, name='playback'),
    path("control/", views.control, name='control'),
    path("", include(router.urls)),
]
