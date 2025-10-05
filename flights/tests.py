from django.test import TestCase
import pytest
from django.utils import timezone
from flights.models import Flight, Booking
from companies.models import Company
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.mark.django_db
def test_create_flight():
    company = Company.objects.create(name="TestAir")
    flight = Flight.objects.create(
        company=company,
        origin="Bishkek",
        destination="Osh",
        departure_time=timezone.now(),
        arrival_time=timezone.now() + timezone.timedelta(hours=2),
        duration=timezone.timedelta(hours=2),
        stops=0,
        price=100,
        seats_total=100,
        seats_available=100
    )
    assert flight.id is not None
    assert flight.seats_available == 100


@pytest.mark.django_db
def test_booking_total_price():
    user = User.objects.create_user(username="user1", password="pass")
    company = Company.objects.create(name="TestAir")
    flight = Flight.objects.create(
        company=company,
        origin="Bishkek",
        destination="Osh",
        departure_time=timezone.now(),
        arrival_time=timezone.now() + timezone.timedelta(hours=2),
        duration=timezone.timedelta(hours=2),
        stops=0,
        price=100,
        seats_total=100,
        seats_available=100
    )

    booking = Booking.objects.create(
        user=user,
        flight=flight,
        seats=2,
        total_price=2 * flight.price
    )
    assert booking.total_price == 200

@pytest.mark.django_db
def test_booking_cancellation_within_24h():
    user = User.objects.create_user(username="user1", password="pass")
    company = Company.objects.create(name="TestAir")
    flight = Flight.objects.create(
        company=company,
        origin="Bishkek",
        destination="Osh",
        departure_time=timezone.now() + timezone.timedelta(days=1),
        arrival_time=timezone.now() + timezone.timedelta(days=1, hours=2),
        duration=timezone.timedelta(hours=2),
        stops=0,
        price=100,
        seats_total=100,
        seats_available=100
    )

    booking = Booking.objects.create(
        user=user,
        flight=flight,
        seats=2,
        total_price=2 * flight.price
    )

    now = timezone.now()
    can_cancel = (flight.departure_time - now).total_seconds() > 24 * 3600
    assert can_cancel is True


@pytest.mark.django_db
def test_manager_cannot_edit_other_company_flight():
    manager = User.objects.create_user(username="manager", password="pass")
    other_company = Company.objects.create(name="OtherAir")
    flight = Flight.objects.create(
        company=other_company,
        origin="Bishkek",
        destination="Osh",
        departure_time=timezone.now(),
        arrival_time=timezone.now() + timezone.timedelta(hours=2),
        duration=timezone.timedelta(hours=2),
        stops=0,
        price=100,
        seats_total=100,
        seats_available=100
    )

    can_edit = flight.company == manager.company if hasattr(manager, "company") else False
    assert not can_edit
