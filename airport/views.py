from django.db.models import Count, F
from rest_framework import viewsets

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Country,
    Crew,
    Flight,
    Location,
    Order,
    Route,
    Ticket,
)

from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    AirportSerializer,
    CountrySerializer,
    CrewSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    FlightSerializer,
    LocationListSerializer,
    LocationRetrieveSerializer,
    LocationSerializer,
    OrderListSerializer,
    OrderSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    RouteSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
    TicketSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return LocationListSerializer
        elif self.action == "retrieve":
            return LocationRetrieveSerializer
        return LocationSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        elif self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related()
                .annotate(
                    seats_available=F(
                        "airplane__seats_in_row"
                    ) * F("airplane__rows") - Count("tickets")
                ).order_by("id")
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related()

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer
