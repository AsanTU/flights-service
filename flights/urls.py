from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("flight/<int:pk>/", views.flight_detail, name="flight_detail"), 
]