import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from datetime import datetime

from .models import Airport, Flight, Passenger, Hotel, FlightBooking, HotelBooking
from decimal import Decimal


def index(request): 
    airports = Airport.objects.all()
    return render(request, "booking/index.html", {
        "airports": airports
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "booking/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "booking/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username    = request.POST["username"]
        email       = request.POST["email"]

        # Ensure password matches confirmation
        password        = request.POST["password"]
        confirmation    = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "booking/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "booking/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "booking/register.html")


def flightSearch(request):
    if request.method == 'POST':
        #Read values entered by the users from the screen
        fromAirportCode = request.POST.get('from')
        toAirportCode   = request.POST.get('to')
        departDate      = request.POST.get('depart-date')
        returnDate      = request.POST.get('return-date')
        inboundStatus   = request.POST.get('inbound-exists')
        numPassengers   = request.POST.get('num-passengers')
        
        #Get origin and destination Airport objects
        fromAirport = Airport.objects.get(code=fromAirportCode)
        toAirport   = Airport.objects.get(code=toAirportCode)

        #Get the list of flights from origin and destination airports
        outboundFlights = list(Flight.objects.filter(origin=fromAirport, destination=toAirport, date=departDate))
        inboundFlights  = list(Flight.objects.filter(origin=toAirport, destination=fromAirport, date=returnDate))

        return render(request, "booking/flightsearch.html", {
            "fromAirport"    : fromAirport, 
            "toAirport"      : toAirport,
            "outboundFlights": outboundFlights,
            "inboundFlights" : inboundFlights,
            "departDate"     : departDate,
            "returnDate"     : returnDate,
            "inboundStatus"  : inboundStatus,
            "numPassengers"  : numPassengers,
            "user"           : request.user
        })
    
    return HttpResponseRedirect(reverse("index"))

@login_required
def tripSummary(request):
    try:
        if request.method == 'POST':
            outboundFlight      = request.POST.get('outbound-flight')
            inboundStatus       = request.POST.get('inbound-exists')
            numPassengers       = request.POST.get('num-passengers')
            outboundFlightObj   = Flight.objects.filter(pk=outboundFlight).first()
            totalAmount         = int(numPassengers) * outboundFlightObj.price 
            
            parameterArray = {
                "outboundFlight"        : outboundFlightObj,
                "numPassengersRange"    : range(1, int(numPassengers)+1),
                "numPassengers"         : int(numPassengers),
                "inboundStatus"         : inboundStatus,                
            }

            if inboundStatus == "true":
                inboundFlight    = request.POST.get('inbound-flight')
                inboundFlightObj = Flight.objects.filter(pk=inboundFlight).first()
                totalAmount     += int(numPassengers) * inboundFlightObj.price 
                parameterArray.update({"inboundFlight": inboundFlightObj})
            
            parameterArray.update({
                "totalAmount"       : totalAmount,
                "tax"               : str(round(totalAmount * 0.085, 2)),
                "totalAmountPlusTax": str(round(totalAmount * 1.085, 2))
            })

            return render(request, "booking/tripsummary.html", parameterArray)
        return HttpResponseRedirect(reverse("index"))
     
    except:
        print("Error while booking the flights.")

@login_required
def processbooking(request):    
    if request.method == 'POST':
        numPassengers           = request.POST.get('numPassengers')
        inboundStatus           = request.POST.get('inboundStatus')
        totalAmount             = request.POST.get('totalAmount')
      
        outboundFlightId    = request.POST.get('outboundFlight.id') 
        parameterArray = {
            "outboundFlightId"      : outboundFlightId,
            "numPassengersRange"    : range(1, int(numPassengers)+1),
            "numPassengers"         : numPassengers,
            "inboundStatus"         : inboundStatus,
            "totalAmount"           : totalAmount
        }

        if inboundStatus == "true":
            inboundFlight    = request.POST.get('inboundFlight.id')
            parameterArray.update({"inboundFlightId": inboundFlight})
        
        return render(request, "booking/processbooking.html",parameterArray)
    return HttpResponseRedirect(reverse("index"))

@login_required
def flightBooking(request):
    if request.method == 'POST':
        inboundStatus       = request.POST.get('inboundStatus')
        numPassengers       = request.POST.get('numPassengers')
        numberPassengers    = int(numPassengers)
        totalAmount         = request.POST.get('totalAmount')
        
        # Create FlightBooking object for the current user
        trip  = FlightBooking.objects.create(user=request.user) 
        trip.totalAmount    = Decimal(totalAmount)

        #Create departure flight object
        outboundFlightId    = request.POST.get('outboundFlight.id') 
        outboundFlight      = Flight.objects.filter(id=outboundFlightId).first()
        trip.flights.add(outboundFlight)
        parameterArray = {
            "inboundStatus"  : inboundStatus,
            "outboundFlight" : outboundFlight
        }
            
        #If round trip, create return flight object
        if inboundStatus == "true":
            inboundFlightId     = request.POST.get('inboundFlight.id') 
            inboundFlight       = Flight.objects.filter(id=inboundFlightId).first()
            trip.flights.add(inboundFlight)
            parameterArray.update({"inboundFlight":inboundFlight})

        count = 1
        while count <= numberPassengers:
            strCount    = str(count)
            firstName   = request.POST.get('first-name-' + strCount)
            lastName    = request.POST.get('last-name-' + strCount)
            birthDate   = request.POST.get('date-of-birth-' + strCount)
        
            passenger   = Passenger.objects.create(first=firstName,last=lastName,dateOfBirth=birthDate)
            passenger.flights.add(outboundFlight)
            if inboundStatus == "true":
                passenger.flights.add(inboundFlight)
            passenger.save()
            trip.passengers.add(passenger)
            count += 1
        
        trip.save()
        #parameterArray.update({"passengers": trip.passengers.all(), "flightExists": True})
        #return render(request, "booking/mybookings.html", parameterArray)
    return myBooking(request)


@login_required
def hotelBooking(request):
    if request.method == "POST":
        duration        = request.POST.get('stay-duration')
        checkinDate     = request.POST.get('checkin-date')
        checkoutDate    = request.POST.get('checkout-date')
        amountPaid      = request.POST.get('amount-paid')
        name            = request.POST.get('hotel-name')
        hotel           = Hotel.objects.filter(name=name).first()
      
        trip            = HotelBooking.objects.create(user=request.user, checkIn=checkinDate, checkOut=checkoutDate)
        trip.hotel.add(hotel)
        trip.totalAmount = amountPaid
        trip.save()

        return myBooking(request)
    return HttpResponseRedirect(reverse("hotelindex"))
    """
        parameterArray = {
            "name"        : name,
            "duration"    : duration,
            "checkinDate" : checkinDate,
            "checkoutDate": checkoutDate,
            "hotelExists" : True
        }
    
    return render(request, "booking/mybookings.html", parameterArray)
    """

def hotelIndex(request):
    hotelCities = Hotel.objects.values('city').distinct()
    return render(request, "booking/hotelindex.html", {
        "hotelCities": hotelCities
    })

def hotelSearch(request):
    if request.method == "POST":
        city            = request.POST.get("hotel-location")
        checkInDate     = request.POST.get("checkin-date")
        checkInDateStr  = datetime.strptime(checkInDate, "%Y-%m-%d").date()
        checkOutDate    = request.POST.get("checkout-date")
        checkOutDateStr = datetime.strptime(checkOutDate, "%Y-%m-%d").date()

        hotels = Hotel.objects.filter(city=city)
        delta = (checkOutDateStr - checkInDateStr).days
        

        return render(request, "booking/hotelsearch.html", {
            "hotels"      : hotels,
            "city"        : city,
            "delta"       : delta,
            "checkInDate" : checkInDate,
            "checkOutDate": checkOutDate,
        })
    return HttpResponseRedirect(reverse("hotelindex"))

@login_required
def hotelSummary(request):
    if request.method == "POST":
        hotelId         = request.POST.get("hotel-id")
        duration        = request.POST.get("hotel-stay-duration")
        checkInDate     = request.POST.get("hotel-checkin")
        checkOutDate    = request.POST.get("hotel-checkout")

        hotel           = Hotel.objects.filter(pk=hotelId).first()
        price           = hotel.price
        cost            = price * int(duration)
        tax             = cost * 0.085
        costAfterTax    = cost * 1.085

        checkInDateDisplay  = datetime.strptime(checkInDate, "%Y-%m-%d").date()
        checkOutDateDisplay = datetime.strptime(checkOutDate, "%Y-%m-%d").date()


        parameterArray = {
            "hotel"                 : hotel,
            "duration"              : duration,
            "checkInDate"           : checkInDate,
            "checkOutDate"          : checkOutDate,
            "checkInDateDisplay"    : checkInDateDisplay,
            "checkOutDateDisplay"   : checkOutDateDisplay,
            "price"                 : price,
            "cost"                  : str(round(cost, 2)),
            "tax"                   : str(round(tax, 2)),
            "costAfterTax"          : str(round(costAfterTax, 2))
        }

        return render(request, "booking/hotelsummary.html", parameterArray)
    return HttpResponseRedirect(reverse("hotelindex"))
          
@login_required
def myBooking(request):
    requestUser = request.user
    parameterArray = {}
    flightExists = False
    hotelExists = False

    try:
        trip            = FlightBooking.objects.filter(user=requestUser).last()
        flightExists    = True
        parameterArray.update({"passengers": trip.passengers.all()})
        flights         = trip.flights.all()
        outboundFlight  = flights.first()
        inboundStatus   = "false"
        parameterArray.update({
            "outboundFlight": outboundFlight,
            "flightExists"  : flightExists
            })

        if len(flights) > 1:
            inboundFlight   = flights.last()
            inboundStatus   = "true"
            parameterArray.update({"inboundFlight": inboundFlight}) 
    
        parameterArray.update({"inboundStatus": inboundStatus})

    except:
        print("No flight booking exists.")

    try:
        hotelBooking   = HotelBooking.objects.filter(user=requestUser)
        
        if len(hotelBooking) > 0:
            hotelExists    = True
            
        recentHotelBooking = hotelBooking.last()
        parameterArray.update({"hotelBooking": hotelBooking.last()})
        parameterArray.update({"hotelExists": hotelExists})
    except:
        print("No hotel booking exists.")

    return render(request, "booking/mybookings.html", parameterArray)
