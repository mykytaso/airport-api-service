import rest_framework.permissions
from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins

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
    OrderSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    RouteSerializer,
    OrderListRetrieveSerializer,
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset

        airplane_type = self.request.query_params.get("type", None)
        if airplane_type:
            queryset = queryset.filter(name__icontains=airplane_type)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "type",
                type={"type": "str"},
                description="Filter by type name (ex. ?type=Aircraft)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("airplane_type")
        return queryset


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

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related()
        return queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        elif self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset

        cities = self.request.query_params.get("city", None)
        if cities:
            queryset = queryset.filter(location__city__icontains=cities)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related()

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "city",
                type={"city": "str"},
                description="Filter airports by city name (ex. ?city=Berlin)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related()
        return queryset


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

        origin = self.request.query_params.get("origin", None)
        if origin:
            queryset = queryset.filter(
                route__origin__location__city__icontains=origin
            )

        destination = self.request.query_params.get("destination", None)
        if destination:
            queryset = queryset.filter(
                route__destination__location__city__icontains=destination
            )

        if self.action == "list":
            queryset = (
                queryset
                .select_related()
                .prefetch_related("crew")
                .annotate(
                    seats_available=F(
                        "airplane__seats_in_row"
                    ) * F("airplane__rows") - Count("tickets")
                ).order_by("id")
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related().prefetch_related("crew")

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "origin",
                type=str,
                description="Filter flights by the origin "
                            "city name (ex.: ?origin=Berlin)",
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description="Filter flights by the destination "
                            "city name (ex.: ?destination=New-York)",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   ):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__flight__route__origin__location__country",
                "tickets__flight__route__destination__location__country",
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListRetrieveSerializer
        return OrderSerializer
