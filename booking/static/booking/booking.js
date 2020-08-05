// Validates if a user's Flight Search inputs are valid
function validateSearchFlight() {

    // Get From and To airports
    let fromSel = document.getElementById('from');
    let toSel   = document.getElementById('to');

    let fromSelOption   = fromSel.options[fromSel.selectedIndex];
    let toSelOption     = toSel.options[toSel.selectedIndex];

    // Get Depart and Return dates
    let departDate      = document.getElementById('depart-date').value;
    let returnDate      = document.getElementById('return-date').value;
    let inboundExists   = document.getElementById('inbound-exists').value;

    // If the From and To airports are the same, are blank, or if the Departure date is later than the Return date, then alert error
    if (fromSelOption.value === 'none') {
        alert('Please select a "From" airport.');
        return false;
    } else if (toSelOption.value === 'none') {
        alert('Please select a "To" airport.');
        return false; 
    } else if (fromSelOption.value === toSelOption.value) {
        alert('Please enter unique "From" and "To" airports.');
        return false;
    } else if (inboundExists === "true" && new Date(departDate).getTime() > new Date(returnDate).getTime()) {
        alert('Return date must be after departure date.');
        return false;
    } else {
        return true;
    }
}

// Validates if a user's Hotel Search inputs are valid
function validateSearchHotel() {

    // Get city name and check-in and check-out dates
    let cityName         = document.getElementById('hotel-location').value;
    let checkinDate      = document.getElementById('checkin-date').value;
    let checkoutDate     = document.getElementById('checkout-date').value;

    // If the city is blank or check-in date is later than the check-out date, then alert error
    if (cityName === 'none') {
        alert('Please select a city.');
        return false;
    } else if (new Date(checkinDate).getTime() >= new Date(checkoutDate).getTime()) {
        alert('Check-out date must be after the check-in date.');
        return false;
    } else {
        return true;
    }
}

// Validates if a user's selected flight is valid
function validateSelectedFlight() { 

    // Get inputs
    outboundFlight      = document.getElementById('outbound-flight').value;
    isInboundExisted    = document.getElementById('inbound-exists').value;
    
    // If the departing Flight is none or blank, or if there is a returning Flight that is none or blank, alert an error
    if (outboundFlight === "none" || outboundFlight === '') {
        alert('Please select Departing Flight.');
        return false;
    } else if (isInboundExisted === 'true') {
        inboundFlight   = document.getElementById('inbound-flight').value;
        if (inboundFlight === 'none' || inboundFlight === '') {
            alert('Please select Returning Flight.');
            return false;
        }
    } else { 
        return true;
    }       
}

// Get the selected flight ID, as well as highlight the selected flight with a light sky blue background
function getFlight(id, direction) {
    
    // Allow only one flight per outbound/inbound to be selected
    if (direction === 'outbound') {
        document.querySelector('#outbound-flight').value = id;
        let outboundRows = document.querySelectorAll('*[id^="outbound-flight-"]');
        for (var i = 0; i < outboundRows.length; i++) {
            outboundRows[i].style.backgroundColor = '#F0F8FF';
        }
        document.querySelector(`#outbound-flight-${id}`).style.backgroundColor = 'lightskyblue';
    } else {
        document.querySelector('#inbound-flight').value = id;
        let inboundRows = document.querySelectorAll('*[id^="inbound-flight-"]');
        for (var i = 0; i < inboundRows.length; i++) {
            inboundRows[i].style.backgroundColor = '#F0F8FF';
        }
        document.querySelector(`#inbound-flight-${id}`).style.backgroundColor = 'lightskyblue';
    }
}

// Set the initial dates in date inputs
function getDate() {
    let today       = new Date();
    let todayDate   = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2); 
    document.getElementById('depart-date').value = todayDate
    document.getElementById('depart-date').min   = todayDate

    let nextDay = new Date();
    nextDay.setDate(today.getDate()+1)
    let tomorrowDate = nextDay.getFullYear() + '-' + ('0' + (nextDay.getMonth() + 1)).slice(-2) + '-' + ('0' + nextDay.getDate()).slice(-2);
    document.getElementById('return-date').value = tomorrowDate
    document.getElementById('return-date').value = tomorrowDate

}

// Validate non-nullable inputs on Passenger form
function required() {
   let numberOfPassengers = document.getElementById('numPassengers').value
    for (let i = 1; i <= numberOfPassengers; i++){
        if (document.getElementById('first-name-'+ i).value.length == 0 || 
            document.getElementById('last-name-' + i).value.length == 0 ||
            document.getElementById('date-of-birth-' + i).value.length == 0) {
            alert('Please enter the passenger(s) information.');
            return false;
        }   
    }     	
    return true; 
} 

// Get hotel ID and highlight selected hotel div
function getHotel(hotelId) {
    document.querySelector('#hotel-id').value = hotelId;
    let allHotels = document.querySelectorAll('*[id^="hotel-"]');
    for (var i = 0; i < allHotels.length; i++) {
        allHotels[i].style.backgroundColor = '#F0F8FF';
    }
    document.querySelector(`#hotel-${hotelId}`).style.backgroundColor = 'lightskyblue';
}

// If no hotels selected, alert an error
function validateSelectedHotel() {
    let hotelId = document.querySelector('#hotel-id').value
    if (hotelId === "0") {
        alert('Please select a hotel.');
        return false;
    }
}