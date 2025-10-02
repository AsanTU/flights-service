from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("customer", "Customer"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    def __str__(self):
        return f"{self.username} ({self.role})"

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies")

    def __str__(self):
        return self.name

class Flight(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="flights")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.DurationField()
    stops = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats_total = models.PositiveIntegerField()
    seats_available = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.name}: {self.origin} → {self.destination}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELED", "Canceled"),
        ("REFUNDED", "Refunded"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    passengers_count = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    confirmation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.confirmation_id} ({self.user.username})"

class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="banners/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f"Banner {self.id}"

class FeaturedOffer(models.Model):
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title