from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Flight)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(HotelBooking)
admin.site.register(FlightBooking)
admin.site.register(Hotel)