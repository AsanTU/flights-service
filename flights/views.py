from django.shortcuts import render, get_object_or_404, redirect
from .models import Flight, Banner, FeaturedOffer, Booking, Company
from .forms import FlightSearchForm, BookingForm, RegisterForm, CustomUserCreationForm, FlightForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
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
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from .models import Flight, Banner, FeaturedOffer
from .forms import FlightSearchForm
from django.contrib.auth import get_user_model
import random
import string

def landing(request):
    now = timezone.now()
    flights = Flight.objects.none()
    form = FlightSearchForm(request.GET or None)

    if form.is_valid():
        flights = Flight.objects.filter(is_active=True)
    
        origin = form.cleaned_data.get("origin")
        destination = form.cleaned_data.get("destination")
        date = form.cleaned_data.get("date")
        passengers = form.cleaned_data.get("passengers")
        price_min = form.cleaned_data.get("price_min")
        price_max = form.cleaned_data.get("price_max")
        company = form.cleaned_data.get("company")
        departure_after = form.cleaned_data.get("departure_after")
        departure_before = form.cleaned_data.get("departure_before")
        stops = form.cleaned_data.get("stops")
    
        if origin:
            flights = flights.filter(origin__iexact=origin)
        if destination:
            flights = flights.filter(destination__iexact=destination)
        if date:
            flights = flights.filter(departure_time__date=date)
        if passengers:
            flights = flights.filter(seats_available__gte=passengers)
        if price_min is not None:
            flights = flights.filter(price__gte=price_min)
        if price_max is not None:
            flights = flights.filter(price__lte=price_max)
        if company:
            flights = flights.filter(company=company)
        if departure_after:
            flights = flights.filter(departure_time__gte=departure_after)
        if departure_before:
            flights = flights.filter(departure_time__lte=departure_before)
        if stops is not None:
            flights = flights.filter(stops=stops)
    else:
        print(form.errors)

    upcoming_flights = Flight.objects.filter(
        departure_time__gte=now,
        departure_time__lte=now + timedelta(days=7),
        is_active=True
    ).order_by('departure_time')[:10]

    banners = Banner.objects.all()
    offers = FeaturedOffer.objects.all()

    return render(
        request,
        "landing.html",
        {
            "form": form,
            "flights": flights,
            "banners": banners,
            "offers": offers,
            "upcoming_flights": upcoming_flights,
            "now": now,  
        },
    )

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

            if passengers_count > flight.seats_available:
                messages.error(request, f"На рейсе осталось только {flight.seats_available} мест.")
                return redirect('flight_detail', pk=flight.id)

            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                passengers_count=passengers_count,
                total_price=flight.price * passengers_count,
                status='PENDING'
            )

            flight.seats_available -= passengers_count
            flight.save()

            messages.success(request, "Бронирование успешно создано!")
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
    now = timezone.localtime(timezone.now())
    departure = timezone.localtime(booking.flight.departure_time)

    if departure - now > timedelta(hours=24):
        if booking.status != "CANCELLED":
            flight = booking.flight
            flight.seats_available += booking.passengers_count
            flight.save()

            booking.status = "CANCELLED"
            booking.save()

            messages.success(request, "Бронирование успешно отменено, места возвращены!")
        else:
            messages.warning(request, "Это бронирование уже отменено.")
    else:
        messages.error(request, "Отменить можно только за 24 часа до вылета!")

    return redirect("user_bookings")

class FlightListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Flight
    template_name = 'flights/manager_flight_list.html'

    def test_func(self):
        return is_manager(self.request.user)

class FlightCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flights/flight_form.html'
    success_url = reverse_lazy('flight_list')

    def test_func(self):
        return is_manager(self.request.user)

    def form_valid(self, form):
        company = self.request.user.companies.first()
        form.instance.company = company  
        return super().form_valid(form)

class FlightUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Flight
    fields = ['origin', 'destination', 'departure_time', 'arrival_time',
              'duration', 'stops', 'price', 'seats_total', 'seats_available', 'is_active']
    template_name = 'flights/flight_form.html'
    success_url = '/flights/'

    def test_func(self):
        return is_manager(self.request.user)

    def get_queryset(self):
          company = self.request.user.companies.first()
          return Flight.objects.filter(company=company)

class FlightDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Flight
    template_name = 'flights/flight_confirm_delete.html'
    success_url = reverse_lazy('flight_list')

    def test_func(self):
        return is_manager(self.request.user)

@method_decorator(login_required, name='dispatch')
class ManagerFlightListView(ListView):
    model = Flight
    template_name = "flights/manager_flight_list.html"
    context_object_name = "flights"

    def get_queryset(self):
        company = self.request.user.companies.first()
        print("Company:", company) 
        if company:
            flights = Flight.objects.filter(company=company)
            print("Flights:", flights)
            return flights
        return Flight.objects.none()

@method_decorator(login_required, name='dispatch')
class ManagerFlightCreateView(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = "flights/flight_form.html"
    success_url = reverse_lazy("manager_flight_list")

    def form_valid(self, form):
        company = self.request.user.companies.first()
        form.instance.company = company  
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ManagerFlightUpdateView(UpdateView):
    model = Flight
    form_class = FlightForm
    template_name = "flights/flight_form.html"
    success_url = reverse_lazy("manager_flight_list")

    def get_queryset(self):
        company = self.request.user.companies.first()
        return Flight.objects.filter(company=company)  

@method_decorator(login_required, name='dispatch')
class ManagerFlightDeleteView(DeleteView):
    model = Flight
    template_name = "flights/flight_confirm_delete.html"
    success_url = reverse_lazy("manager_flight_list")

    def get_queryset(self):
        company = self.request.user.companies.first()
        return Flight.objects.filter(company=company) 

def company_stats(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    flights = company.flights.all()

    total_flights = flights.count()
    upcoming = flights.filter(departure_time__gt=timezone.now()).count()
    completed = flights.filter(arrival_time__lt=timezone.now()).count()
    total_passengers = Booking.objects.filter(flight__company=company).aggregate(
        total=Sum('seats_booked')
    )['total'] or 0

    total_revenue = Booking.objects.filter(flight__company=company, status="PAID").aggregate(
        total=Sum(
            ExpressionWrapper(F('seats_booked') * F('flight__price'), output_field=FloatField())
        )
    )['total'] or 0

    context = {
        "company": company,
        "total_flights": total_flights,
        "upcoming": upcoming,
        "completed": completed,
        "total_passengers": total_passengers,
        "total_revenue": total_revenue,
    }
    return render(request, "flights/company_stats.html", context)

@login_required
def dashboard(request):
    user = request.user
    now = timezone.localtime()
    period = request.GET.get("period", "all")

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0)
        end_date = now.replace(hour=23, minute=59, second=59)
    elif period == "week":
        start_date = now
        end_date = now + timedelta(days=7)
    elif period == "month":
        start_date = now
        end_date = now + timedelta(days=30)
    else:
        start_date = None
        end_date = None

    if user.is_staff:  
        flights = Flight.objects.all()
        bookings = Booking.objects.all()
    else:  
        company = user.companies.first()
        if not company:
            return render(request, "flights/manager_dashboard.html", {"error": "У вас нет назначенной компании."})
        flights = company.flights.all()
        flight_ids = flights.values_list('id', flat=True)
        bookings = Booking.objects.filter(flight__id__in=flight_ids)

    if start_date and end_date:
        flights = flights.filter(departure_time__gte=start_date, departure_time__lte=end_date)
        bookings = bookings.filter(flight__departure_time__gte=start_date, flight__departure_time__lte=end_date)

    active_bookings = bookings.filter(status__in=['PENDING', 'PAID'])

    total_flights = flights.count()
    upcoming = flights.filter(departure_time__gte=now).count()
    completed = flights.filter(arrival_time__lt=now).count()
    total_passengers = active_bookings.aggregate(total=Sum('passengers_count'))['total'] or 0
    total_revenue = active_bookings.filter(status="PAID").aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        "period": period,
        "total_flights": total_flights,
        "upcoming": upcoming,
        "completed": completed,
        "total_passengers": total_passengers,
        "total_revenue": total_revenue,
    }

    template = "flights/admin_statistics.html" if user.is_staff else "flights/manager_dashboard.html"
    if not user.is_staff:
        context["company"] = company

    return render(request, template, context)

def flights_list(request):
    return render(request, 'flights/flights_list.html')

def create_flight(request):
    return render(request, 'flights/create_flight.html')

def bookings_list(request):
    return render(request, 'flights/bookings_list.html')

@login_required
def user_bookings(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).select_related('flight')
    now = timezone.localtime()

    status_filter = request.GET.get("status")
    if status_filter == "active":
        bookings = bookings.filter(status__in=['PENDING', 'PAID'], flight__departure_time__gte=now)
    elif status_filter == "past":
        bookings = bookings.filter(flight__departure_time__lt=now)

    for booking in bookings:
        departure = booking.flight.departure_time
        if timezone.is_naive(departure):
            departure = timezone.make_aware(departure, timezone.get_current_timezone())
        booking.departure_str = departure.strftime("%d:%m:%Y %H:%M")
        booking.can_cancel = (departure - now) > timedelta(hours=24) and booking.status in ['PENDING', 'PAID']

    context = {
        'bookings': bookings,
        'status_filter': status_filter
    }
    return render(request, 'flights/user_bookings.html', context)

User = get_user_model()

def is_manager(user):
    return user.is_authenticated and user.role == "manager"

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import User, Booking

@login_required
@user_passes_test(lambda u: u.role == "manager")
def manager_users(request):
    manager_companies = request.user.companies.all()

    booked_users = User.objects.filter(
        bookings__flight__company__in=manager_companies
    ).exclude(id=request.user.id).distinct()

    users_with_bookings = []
    for user in booked_users:
        user_bookings = user.bookings.filter(
            flight__company__in=manager_companies
        ).select_related('flight')
        users_with_bookings.append({
            "user": user,
            "bookings": user_bookings
        })

    return render(request, "manager_users.html", {
        "users_with_bookings": users_with_bookings
    })

from django.utils import timezone
from flights.models import Booking

def upcoming_bookings(request):
    now = timezone.now()
    bookings = Booking.objects.filter(
        flight__departure_time__gte=now,
        notification_sent=False
    )

    data = []
    for booking in bookings:
        data.append({
            "user": booking.user.get_full_name(),
            "email": booking.user.email,
            "flight": f"{booking.flight.origin} → {booking.flight.destination}",
            "departure_time": booking.flight.departure_time,
            "status": booking.status,
            "passengers_count": booking.passengers_count,
        })

    from django.http import JsonResponse
    return JsonResponse(data, safe=False)