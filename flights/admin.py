from django.contrib import admin
from .models import User, Company, Flight, Booking
from .models import Banner, FeaturedOffer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_managers")

    def get_managers(self, obj):
        return ", ".join([u.username for u in obj.managers.all()])
    get_managers.short_description = "Managers"

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("company", "origin", "destination", "departure_time", "arrival_time", "price", "seats_available", "is_active")
    list_filter = ("company", "origin", "destination", "is_active")
    search_fields = ("origin", "destination")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("confirmation_id", "user", "flight", "passengers_count", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("confirmation_id", "user__username")
    readonly_fields = ("confirmation_id", "created_at")

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "order")

@admin.register(FeaturedOffer)
class FeaturedOfferAdmin(admin.ModelAdmin):
    list_display = ("title", "flight")
    search_fields = ("title", "flight__origin", "flight__destination")