from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .api import api


def health(request):
    return HttpResponse("Healthy")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health-check"),
    path("api/v1/", api.urls),
]
