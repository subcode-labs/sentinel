from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("runtime-secret/", views.runtime_secret, name="runtime_secret"),
]
