from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airports/", include("airport.urls", namespace="airport")),
] + debug_toolbar_urls()
