from django.shortcuts import render, get_object_or_404, redirect
from .models import Flight, Banner, FeaturedOffer, Booking, Company
from .forms import FlightSearchForm, BookingForm, RegisterForm, CustomUserCreationForm, FlightForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Sum
from datetime import timedelta, datetime
from .utils import is_manager
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

def landing(request):
    flights = None
    if request.method == "GET":
        form = FlightSearchForm(request.GET)
        if form.is_valid():
            origin = form.cleaned_data["origin"]
            destination = form.cleaned_data["destination"]
            date = form.cleaned_data["date"]
            passengers = form.cleaned_data["passengers"]

            flights = Flight.objects.filter(
                origin__iexact=origin,
                destination__iexact=destination,
                departure_time__date=date,
                seats_available__gte=passengers,
                is_active=True
            )
    else:
        form = FlightSearchForm()

    banners = Banner.objects.all()
    offers = FeaturedOffer.objects.all()
    return render(request, "landing.html", {"form": form, "flights": flights, "banners": banners, "offers": offers})

def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, "flight_detail.html", {"flight": flight})

@login_required
def create_booking(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            passengers_count = form.cleaned_data['passengers_count']
            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                passengers_count=passengers_count,
                total_price=flight.price * passengers_count
            )
            return redirect('checkout_booking', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'flights/create_booking.html', {'form': form, 'flight': flight})

@login_required
def checkout_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.status = 'PAID'
        booking.paid_at = timezone.now()
        booking.save()

        send_mail(
            subject=f"Бронирование {booking.confirmation_id} оплачено",
            message=f"Ваше бронирование на рейс {booking.flight} было успешно оплачено.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
        )

        return redirect('booking_success', booking_id=booking.id)

    return render(request, 'flights/checkout.html', {'booking': booking})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing')
    else:
        form = CustomUserCreationForm()
    return render(request, 'flights/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing') 

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'flights/booking_success.html', {'booking': booking})

@login_required
def user_dashboard(request):
    now = timezone.now()
    user = request.user

    active_bookings = Booking.objects.filter(
        Q(user=user),
        Q(status='PENDING') | Q(status='PAID'),
        flight__departure_time__gte=now
    )

    past_bookings = Booking.objects.filter(
        Q(user=user),
        Q(status='CANCELED') | Q(status='REFUNDED') | Q(status='PAID'),
        flight__departure_time__lt=now
    )

    context = {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'flights/user_dashboard.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    now = timezone.now()

    if booking.flight.departure_time - now > timedelta(hours=24):
        booking.status = 'REFUNDED' 
    else:
        booking.status = 'CANCELED' 

    booking.save()
    return redirect('user_dashboard') 


class FlightListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Flight
    template_name = 'flights/flight_list.html'

    def test_func(self):
        return is_manager(self.request.user)

class FlightCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flights/flight_form.html'
    success_url = reverse_lazy('flight_list')

    def test_func(self):
        return is_manager(self.request.user)

class FlightUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Flight
    fields = ['origin', 'destination', 'departure_time', 'arrival_time', 'price']
    template_name = 'flights/flight_form.html'
    success_url = reverse_lazy('flight_list')

    def test_func(self):
        return is_manager(self.request.user)

class FlightDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Flight
    template_name = 'flights/flight_confirm_delete.html'
    success_url = reverse_lazy('flight_list')

    def test_func(self):
        return is_manager(self.request.user)


def company_stats(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    flights = company.flights.all()

    total_flights = flights.count()
    upcoming = flights.filter(departure_time__gt=timezone.now()).count()
    completed = flights.filter(arrival_time__lt=timezone.now()).count()
    total_passengers = Booking.objects.filter(flight__company=company).count()
    total_revenue = (
        Booking.objects.filter(flight__company=company, status="PAID")
        .aggregate(Sum("flight__price"))["flight__price__sum"] or 0
    )

    context = {
        "company": company,
        "total_flights": total_flights,
        "upcoming": upcoming,
        "completed": completed,
        "total_passengers": total_passengers,
        "total_revenue": total_revenue,
    }
    return render(request, "flights/company_stats.html", context)