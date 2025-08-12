from django.urls import path
from . import views

urlpatterns = [
    path("preview/", views.preview, name='preview'),
    path("history/", views.history, name='history'),
    path("playback/", views.playback, name='playback'),
    path("control/", views.control, name='control'),
]
