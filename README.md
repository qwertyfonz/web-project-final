I created a simulated booking website, where logged in users can book flights and hotels. 

For flights, users can choose from either one-way or round-trip options, for dates extending up until the 1st of February, 2021. 
I used the Airport, Flight, and Passenger models to accomplish this, as well as a FlightBooking object to summarize the aspects of the user's booked flight.

Similarly for hotels, the Hotel object is used with the HotelBooking object as the summary of the booked hotel.

For flights, the directions look like the following:
--> Input search parameters for flight(s) (index.html)
--> Select desired flight(s) (flightsearch.html)
--> Confirm details of flight booking (tripsummary.html)
--> Input passenger information (processbooking.html)
--> Booking complete

For hotels:
--> Input search parameters for hotel (hotelindex.html)
--> Select desired hotel (hotelsearch.html)
--> Confirm details of hotel booking (hotelsummary.html)
--> Booking complete

The functions in views.py correspond with the above functions.

Finally, the My Bookings page (mybookings.html) displays the most recent bookings that the user has made, for both flight and hotels. 
If the user has not made any bookings so far, the page will display "No bookings found."

I originally was going to use real-time APIs to populate my database and make my application feel more real, but it turns out that we need to be paid members
or subscribers to the sites in order to access them, so I ended up needing to limit my choices of destinations (Boston and NYC) and hotels, since I manually inputted them.
For Flight objects, I actually created some sample flights, then used a loop (in Populate Functions.txt) in order to add them for every day into my database.
The Airports JSON file was what I was originally working with, before I decided to cut it down to only BOS, JFK, and LGA Airports, and the list of hotels are in the Hotels JSON file.

