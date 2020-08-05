import json, random
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import *


class User(AbstractUser):
    pass

class Airport(models.Model):
    code    = models.CharField(max_length=3)
    name    = models.CharField(max_length=64)
    city    = models.CharField(max_length=64)
    state   = models.CharField(max_length=64)

def random_num():
    return random.randint(100,200)

class Flight(models.Model):
    origin          = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures", null=True)
    destination     = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals", null=True)
    date            = models.DateField(default=date.today)
    carrier         = models.CharField(max_length=64) 
    departureTime   = models.TimeField(default=time(12,00))
    arrivalTime     = models.TimeField(default=time(12,00))
    carrier         = models.CharField(max_length=64)
    duration        = models.IntegerField(default=0)
    price           = models.IntegerField(default=random_num)

  
class Passenger(models.Model):
    first           = models.CharField(max_length=64)
    last            = models.CharField(max_length=64)
    dateOfBirth     = models.DateField(default=date.today) 
    flights         = models.ManyToManyField(Flight)


class FlightBooking(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    passengers      = models.ManyToManyField(Passenger) 
    flights         = models.ManyToManyField(Flight)
    totalAmount     = models.DecimalField(max_digits=6, decimal_places=2, default=0)

class Hotel(models.Model):
    name    = models.CharField(max_length=100)
    city    = models.CharField(max_length=64)
    address = models.CharField(max_length=100)
    price   = models.IntegerField(default=0)
    image   = models.URLField()  


class HotelBooking(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel           = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    checkIn         = models.DateField()
    checkOut        = models.DateField()
    totalAmount     = models.DecimalField(max_digits=6, decimal_places=2, default=0)
