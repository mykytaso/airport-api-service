from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airports/", include("airport.urls", namespace="airport")),
]
