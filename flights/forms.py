from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Booking, Flight, Company

class FlightSearchForm(forms.Form):
    # origin = forms.CharField(max_length=100, label="Откуда")
    # destination = forms.CharField(max_length=100, label="Куда")
    # date = forms.DateField(
    #     widget=forms.DateInput(attrs={"type": "date"}), 
    #     label="Дата вылета"
    # )
    # passengers = forms.IntegerField(min_value=1, label="Количество пассажиров")

    origin = forms.CharField(required=False)
    destination = forms.CharField(required=False)
    date = forms.DateField(required=False)
    passengers = forms.IntegerField(required=False)

    price_min = forms.IntegerField(required=False, label="Мин. цена")
    price_max = forms.IntegerField(required=False, label="Макс. цена")

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(), 
        required=False, 
        label="Авиакомпания"
    )

    departure_after = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Вылет после"
    )
    departure_before = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Вылет до"
    )

    stops = forms.IntegerField(required=False, label="Пересадки (0 = прямой)")

class BookingForm(forms.Form):
    passengers_count = forms.IntegerField(min_value=1, label="Количество пассажиров")

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = [
            'origin', 'destination', 'departure_time', 'arrival_time',
            'duration', 'stops', 'price', 'seats_total', 'seats_available', 'is_active', 'flight_class', 'return_flight'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }