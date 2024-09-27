from django.db import transaction
from rest_framework import serializers

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


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "capacity",
            "image"
        )
        read_only_fields = ("image",)


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False)


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name",)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name",)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ("id", "city", "country")


class LocationListSerializer(LocationSerializer):
    country = serializers.CharField(
        source="country.name",
        read_only=False,
    )


class LocationRetrieveSerializer(LocationSerializer):
    country = CountrySerializer(many=False, read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "location")


class AirportRetrieveSerializer(AirportSerializer):
    location = LocationRetrieveSerializer(many=False, read_only=True)


class AirportListSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="location.city", read_only=True)
    country = serializers.CharField(source="location.country", read_only=True)

    class Meta:
        model = Airport
        fields = ("id", "name", "city", "country")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "origin", "destination", "distance")

    def validate(self, attrs):
        Route.validate_origin_destination_not_be_the_same(
            attrs["origin"],
            attrs["destination"],
            serializers.ValidationError,
        )
        return attrs


class RouteListSerializer(RouteSerializer):
    origin = serializers.CharField(source="origin.__str__", read_only=False)
    destination = serializers.CharField(
        source="destination.__str__",
        read_only=False,
    )


class RouteRetrieveSerializer(RouteSerializer):
    origin = AirportListSerializer(many=False, read_only=True)
    destination = AirportListSerializer(many=False, read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "crew",
            "route",
            "departure_time",
            "arrival_time",
        )

    def validate(self, attrs):
        Flight.validate_departure_time_not_later_arrival_time(
            attrs["departure_time"],
            attrs["arrival_time"],
            serializers.ValidationError,
        )
        return attrs


class FlightListSerializer(serializers.ModelSerializer):
    airplane = serializers.CharField(source="airplane.__str__", read_only=True)
    route = serializers.CharField(source="route.__str__", read_only=True)
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "route",
            "departure_time",
            "arrival_time",
            "seats_available",
        )


class FlightRetrieveSerializer(serializers.ModelSerializer):
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )
    route = RouteListSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="row_and_seat",
        source="tickets",
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "crew",
            "route",
            "departure_time",
            "arrival_time",
            "taken_seats",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat", "flight",)

    def validate(self, attrs):
        Ticket.validate_seat(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane.rows,
            attrs["flight"].airplane.seats_in_row,
            serializers.ValidationError,
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = serializers.CharField(source="flight.__str__", read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListRetrieveSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
