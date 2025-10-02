from django.shortcuts import render, get_object_or_404
from .models import Flight, Banner, FeaturedOffer
from .forms import FlightSearchForm
from django.utils import timezone

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