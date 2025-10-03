from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view

urlpatterns = [
    path("", views.landing, name="landing"),
    path("flight/<int:pk>/", views.flight_detail, name="flight_detail"), 
    path("flight/<int:flight_id>/book/", views.create_booking, name="create_booking"),
    path('booking/<int:booking_id>/checkout/', views.checkout_booking, name='checkout_booking'),
    path('login/', auth_views.LoginView.as_view(template_name='flights/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('flights/', views.FlightListView.as_view(), name='flight_list'),
    path('flights/add/', views.FlightCreateView.as_view(), name='flight_create'),
    path('flights/<int:pk>/edit/', views.FlightUpdateView.as_view(), name='flight_update'),
    path('flights/<int:pk>/delete/', views.FlightDeleteView.as_view(), name='flight_delete'),
    path("company/<int:company_id>/stats/", views.company_stats, name="company_stats"),
]