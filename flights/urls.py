from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view, FlightListView, FlightCreateView, FlightUpdateView, FlightDeleteView, ManagerFlightListView, ManagerFlightCreateView, ManagerFlightUpdateView, ManagerFlightDeleteView

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
    path('flights/all', views.flights_list, name='flights_list'),
    path('flights/add/', views.FlightCreateView.as_view(), name='flight_add'),
    path('flights/<int:pk>/edit/', views.FlightUpdateView.as_view(), name='flight_update'),
    path('flights/<int:pk>/delete/', views.FlightDeleteView.as_view(), name='flight_delete'),
    path("company/<int:company_id>/stats/", views.company_stats, name="company_stats"),
    path('manager/', views.dashboard, name='manager_dashboard'),
    path('flights/create/', views.create_flight, name='create_flight'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('flights/', FlightListView.as_view(), name='manager_flight_list'), 
    path("manager/flights/", ManagerFlightListView.as_view(), name="manager_flight_list"),
    path("manager/flights/add/", ManagerFlightCreateView.as_view(), name="manager_flight_add"),
    path("manager/flights/<int:pk>/edit/", ManagerFlightUpdateView.as_view(), name="manager_flight_edit"),
    path("manager/flights/<int:pk>/delete/", ManagerFlightDeleteView.as_view(), name="manager_flight_delete"),
    path('statistics/', views.dashboard, name='statistics'),
    path("manager/users/", views.manager_users, name="manager_users"),
    path('api/upcoming-bookings/', views.upcoming_bookings, name='upcoming_bookings'),
]