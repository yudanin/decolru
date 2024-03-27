from django.urls import path
from . import views

urlpatterns = [
    path("", views.cmsadmin, name="cms-admin")
]