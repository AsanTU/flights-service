from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Booking, Flight

class FlightSearchForm(forms.Form):
    origin = forms.CharField(max_length=100, label="Откуда")
    destination = forms.CharField(max_length=100, label="Куда")
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата вылета")
    passengers = forms.IntegerField(min_value=1, label="Количество пассажиров")

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
            'company', 'origin', 'destination', 'departure_time', 'arrival_time',
            'duration', 'stops', 'price', 'seats_total', 'seats_available', 'is_active'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }