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

from .models import User, Airport, Flight, Passenger, Hotel, FlightBooking, HotelBooking
from decimal import Decimal


# Displays index page (Flight Search)
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

# Takes input from the index (Flight Search) page and return a list of results that matches the user's search terms
def flightSearch(request):
    if request.method == 'POST':

        # Get inputs
        fromAirportCode = request.POST.get('from')
        toAirportCode   = request.POST.get('to')
        departDate      = request.POST.get('depart-date')
        returnDate      = request.POST.get('return-date')
        inboundStatus   = request.POST.get('inbound-exists')
        numPassengers   = request.POST.get('num-passengers')
        
        # Get origin and destination Airport objects
        fromAirport = Airport.objects.get(code=fromAirportCode)
        toAirport   = Airport.objects.get(code=toAirportCode)

        # Get the list of flights from origin and destination airports
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
    
    # If the user refreshes the page, return back to the main page
    return HttpResponseRedirect(reverse("index"))

 # After selecting a flight, allow the user to see the summary of what they are about to book
@login_required
def tripSummary(request):
    try:
        if request.method == 'POST':

            # Get inputs
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

            # If there is a returning flight
            if inboundStatus == "true":
                inboundFlight    = request.POST.get('inbound-flight')
                inboundFlightObj = Flight.objects.filter(pk=inboundFlight).first()
                totalAmount     += int(numPassengers) * inboundFlightObj.price 
                parameterArray.update({"inboundFlight": inboundFlightObj})
            
            # Add cost variables to what we are passing to the template
            parameterArray.update({
                "totalAmount"       : totalAmount,
                "tax"               : str(round(totalAmount * 0.085, 2)),
                "totalAmountPlusTax": str(round(totalAmount * 1.085, 2))
            })

            return render(request, "booking/tripsummary.html", parameterArray)
        
        # If the user refreshes the page, return back to the main page
        return HttpResponseRedirect(reverse("index"))
     
    except:
        print("Error while booking the flights.")

# Render form for user to put in passenger information
@login_required
def processbooking(request):    
    if request.method == 'POST':

        # Get inputs
        numPassengers           = request.POST.get('numPassengers')
        inboundStatus           = request.POST.get('inboundStatus')
        totalAmount             = request.POST.get('totalAmount')
        outboundFlightId        = request.POST.get('outboundFlight.id') 

        parameterArray = {
            "outboundFlightId"      : outboundFlightId,
            "numPassengersRange"    : range(1, int(numPassengers)+1),
            "numPassengers"         : numPassengers,
            "inboundStatus"         : inboundStatus,
            "totalAmount"           : totalAmount
        }

        # If there is a returning flight, also add info about the returning flight
        if inboundStatus == "true":
            inboundFlight    = request.POST.get('inboundFlight.id')
            parameterArray.update({"inboundFlightId": inboundFlight})
        
        return render(request, "booking/processbooking.html", parameterArray)
    
    # If the user refreshes the page, return back to the main page
    return HttpResponseRedirect(reverse("index"))

# Save the flight as a FlightBooking object
@login_required
def flightBooking(request):
    if request.method == 'POST':

        # Get inputs
        inboundStatus       = request.POST.get('inboundStatus')
        numPassengers       = request.POST.get('numPassengers')
        numberPassengers    = int(numPassengers)
        totalAmount         = request.POST.get('totalAmount')
        
        # Create FlightBooking object for the current user
        trip  = FlightBooking.objects.create(user=request.user) 
        trip.totalAmount    = Decimal(totalAmount)

        # Add departing Flight
        outboundFlightId    = request.POST.get('outboundFlight.id') 
        outboundFlight      = Flight.objects.filter(id=outboundFlightId).first()
        trip.flights.add(outboundFlight)
        parameterArray = {
            "inboundStatus"  : inboundStatus,
            "outboundFlight" : outboundFlight
        }
            
        # If round trip, add returning Flight
        if inboundStatus == "true":
            inboundFlightId     = request.POST.get('inboundFlight.id') 
            inboundFlight       = Flight.objects.filter(id=inboundFlightId).first()
            trip.flights.add(inboundFlight)
            parameterArray.update({"inboundFlight":inboundFlight})

        # Add user-entered passenger info into the FlightObject
        count = 1
        while count <= numberPassengers:
            strCount    = str(count)
            firstName   = request.POST.get('first-name-' + strCount)
            lastName    = request.POST.get('last-name-' + strCount)
            birthDate   = request.POST.get('date-of-birth-' + strCount)

            # Create a new Passenger object and associate departing Flight with passenger
            passenger   = Passenger.objects.create(first=firstName,last=lastName,dateOfBirth=birthDate)
            passenger.flights.add(outboundFlight)

            # If round trip, add returning Flight association
            if inboundStatus == "true":
                passenger.flights.add(inboundFlight)
            passenger.save()

            # Add Passenger to the FlightBooking
            trip.passengers.add(passenger)
            count += 1
        
        # Save the FlightObject
        trip.save()

    # Run the myBooking function (see below)    
    return myBooking(request)

# Render Hotel Search page (like index page for Flight Search)
def hotelIndex(request):
    hotelCities = Hotel.objects.values('city').distinct()
    return render(request, "booking/hotelindex.html", {
        "hotelCities": hotelCities
    })

# Takes input from the index (Hotel Search) page and return a list of results that matches the user's search terms
def hotelSearch(request):
    if request.method == "POST":

        # Get inputs
        city            = request.POST.get("hotel-location")
        checkInDate     = request.POST.get("checkin-date")
        checkInDateStr  = datetime.strptime(checkInDate, "%Y-%m-%d").date()
        checkOutDate    = request.POST.get("checkout-date")
        checkOutDateStr = datetime.strptime(checkOutDate, "%Y-%m-%d").date()

        # Filter Hotels by city name
        hotels = Hotel.objects.filter(city=city)

        # Find the duration of the stay (from check-in to check-out)
        delta = (checkOutDateStr - checkInDateStr).days
        
        return render(request, "booking/hotelsearch.html", {
            "hotels"      : hotels,
            "city"        : city,
            "delta"       : delta,
            "checkInDate" : checkInDate,
            "checkOutDate": checkOutDate,
        })

    # If the user refreshes the page, return back to the main page
    return HttpResponseRedirect(reverse("hotelindex"))
   
# After selecting a hotel, allow the user to see the summary of what they are about to book
@login_required
def hotelSummary(request):
    if request.method == "POST":
        
        # Get inputs
        hotelId         = request.POST.get("hotel-id")
        duration        = request.POST.get("hotel-stay-duration")
        checkInDate     = request.POST.get("hotel-checkin")
        checkOutDate    = request.POST.get("hotel-checkout")

        # Find the Hotel object and cost to book that hotel for the intended stay
        hotel           = Hotel.objects.filter(pk=hotelId).first()
        price           = hotel.price
        cost            = price * int(duration)
        tax             = cost * 0.085
        costAfterTax    = cost * 1.085

        # Convert inputted dates into strings
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
    
    # If the user refreshes the page, return back to the main page
    return HttpResponseRedirect(reverse("hotelindex"))

# Save the hotel as a HotelBooking object
@login_required
def hotelBooking(request):
    if request.method == "POST":

        # Get inputs
        duration         = request.POST.get('stay-duration')
        checkinDate      = request.POST.get('checkin-date')
        checkoutDate     = request.POST.get('checkout-date')
        amountPaid       = request.POST.get('amount-paid')
        name             = request.POST.get('hotel-name')
        hotel            = Hotel.objects.filter(name=name).first()

        # Create new HotelBooking object
        trip             = HotelBooking.objects.create(user=request.user, checkIn=checkinDate, checkOut=checkoutDate)
        trip.hotel       = hotel
        trip.totalAmount = amountPaid

        # Save HotelBooking object
        trip.save()

        # Run the myBooking function (see below)
        return myBooking(request)

     # If the user refreshes the page, return back to the main page   
    return HttpResponseRedirect(reverse("hotelindex"))

# Display to the user their most recent bookings
@login_required
def myBooking(request):
    requestUser = request.user
    flightExists = False
    hotelExists = False
    parameterArray = {
        "flightExists" : flightExists,
        "hotelExists"  : hotelExists 
        }

    # Check if a FlightBooking object exists for the logged in user and get associated values
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

        # If there is more than one Flight in the trip, it must be a returning Flight 
        if len(flights) > 1:
            inboundFlight   = flights.last()
            inboundStatus   = "true"
            parameterArray.update({"inboundFlight": inboundFlight}) 
    
        parameterArray.update({"inboundStatus": inboundStatus})
    except:
        print("No flight booking exists.")

    # Check if a HotelBooking object exists for the logged in user and get associated values
    try:
        hotelBooking   = HotelBooking.objects.filter(user=requestUser)
        
        # If it exists, the length should be greater than 0
        if len(hotelBooking) > 0:
            hotelExists    = True

        # Get the most recent HotelBooking       
        recentHotelBooking = hotelBooking.last()
        parameterArray.update({"hotelBooking": hotelBooking.last()})
        parameterArray.update({"hotelExists": hotelExists})
    except:
        print("No hotel booking exists.")

    return render(request, "booking/mybookings.html", parameterArray)
