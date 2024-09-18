from django.db import models
from django.db.models import UniqueConstraint

from airport_api_service import settings


class AirplaneType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=64)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Country(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class City(models.Model):
    city = models.CharField(max_length=64)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities",
    )

    def __str__(self):
        return f"{self.city}, {self.country}"


class Airport(models.Model):
    name = models.CharField(max_length=64)
    location = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports",
    )

    def __str__(self):
        return f"{self.name} ({self.location})"


class Route(models.Model):
    origin = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="origin_routes",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes",
    )
    distance = models.IntegerField()

    def __str__(self):
        return (f"{self.origin} -> {self.destination} "
                f"| Distance: {self.distance}")


class Flight(models.Model):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="flights")
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return (f"{self.route.origin.location}: {self.departure_time} -> "
                f"{self.route.destination.location}: {self.arrival_time}, "
                f"Airplane: {self.airplane}")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "flight"],
                name="unique_ticket_row_seat_flight",
            ),
        ]
        ordering = ['row', 'seat',]

    def __str__(self):
        return f"Row: {self.row} Seat: {self.seat}, Flight: {self.flight}"

    @staticmethod
    def validate_seat(
            ticket_row: int,
            ticket_seat: int,
            airplane_row: int,
            airplane_seats_in_row: int,
            error_to_raise,
    ):
        if not (1 <= ticket_row <= airplane_row):
            raise error_to_raise(
                {
                    "row": (
                        f"Row must be between 1 and {airplane_row}, "
                        f"not {ticket_row}"
                    )
                }
            )

        if not (1 <= ticket_seat <= airplane_seats_in_row):
            raise error_to_raise(
                {
                    "seat": (
                        f"seat must be between 1 and {airplane_seats_in_row}, "
                        f"not {ticket_seat}"
                    )
                }
            )

    def clean(self):
        Ticket.validate_seat(
            self.row,
            self.seat,
            self.flight.airplane.rows,
            self.flight.airplane.seats_in_row,
            ValueError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields,
        )
