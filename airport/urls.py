from django.urls import path, include
from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
    OrderViewSet,
    TicketViewSet,
)

from rest_framework import routers

app_name = "airport"

router = routers.DefaultRouter()

router.register("airplane_types", AirplaneTypeViewSet,)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("countries", CountryViewSet)
router.register("city", CityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
