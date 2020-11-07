from rest_framework.routers import DefaultRouter
from phone_verify.api import VerificationViewSet

from django.urls import path, include

from . import views 

default_router = DefaultRouter(trailing_slash=False)
default_router.register('phone', VerificationViewSet, basename='phone')

urlpatterns = [
    path('', include(default_router.urls)),
]