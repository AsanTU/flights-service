from django import forms

class FlightSearchForm(forms.Form):
    origin = forms.CharField(max_length=100, label="Откуда")
    destination = forms.CharField(max_length=100, label="Куда")
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Дата вылета")
    passengers = forms.IntegerField(min_value=1, label="Количество пассажиров")