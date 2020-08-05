from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("flightsearch", views.flightSearch, name="flightsearch"),
    path("tripsummary", views.tripSummary, name="tripsummary"),
    path("processbooking", views.processbooking, name="processbooking"),
    path("flightbooking", views.flightBooking, name="flightbooking"),
    path("hotelindex", views.hotelIndex, name="hotelindex"),
    path("hotelsearch", views.hotelSearch, name="hotelsearch"),
    path("hotelsummary", views.hotelSummary, name="hotelsummary"),
    path("hotelbooking", views.hotelBooking, name="hotelbooking"),
    path("mybooking", views.myBooking, name="mybooking")
]