import json
from fastapi import FastAPI, HTTPException
from models import StudioRentalInput, ConfirmPaymentInput # ung asa models ko
from datetime import date

app = FastAPI(title="LA School of Rock - Management API")

# --- Helper functions to read and save data.json ---
def load_data():
    with open("data.json", "r") as file:
        return json.load(file)

def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=2)


# - - - - - - - - - - - - - - Studio Rental API - - - - - - - - - - - - - -  #         

# --- 1. READ: Get all Studio Bookings (GET) ---
@app.get("/studio-rentals", status_code=200)
def get_studio_rentals():
    data = load_data()
    return data["studio_rentals"] # eto ung ilalagay sa terminal\
        # studio_rentals come's from the json data title



# --- 2. CREATE: Add a new Studio Booking (POST) ---
@app.post("/studio-rentals", status_code=201)
def create_studio_rental(booking: StudioRentalInput): # base on the modeled created
    #the booking is from the new_booking inside the main.py
    data = load_data() # load the data from data.json
    rentals = data["studio_rentals"] #this is where it will get stored

    # Get the hourly rate from settings
    hourly_rate = data["settings"]["studio_hourly_rate"] # from the data.json and settings and hourly rate data

    # Auto-increment ID
    new_id = max([r["id"] for r in rentals], default=0) + 1
    #max gets the latest id then add 1

    new_rental = {
        "id": new_id, # auto incremented
        "client_name": booking.client_name,
        "contact_number": booking.contact_number,
        "date_issued": str(date.today()), 
        "date": booking.date,
        "start_time": booking.start_time,
        "hours": booking.hours,
        "total_fee": booking.hours * hourly_rate,   # <-- automatic calculation
        "status": "Booked"
    }

    rentals.append(new_rental) # rentals which is the studio rentals, then saves the new rental data
    save_data(data) # saved the progress
    return new_rental # sends this as the response for the postman or terminal


# --- 3. FINISH & PAY: update the status (PATCH) ---
@app.patch("/studio-rentals/{rental_id}/pay", status_code=200)
def pay_studio_rental(rental_id: int, payment: ConfirmPaymentInput):
    data = load_data()
    rentals = data["studio_rentals"]
    transactions = data["transactions"]
    
    # for finding the id
    for r in rentals:
        if r["id"] == rental_id:
            if r["status"] == "Paid":
                raise HTTPException(status_code=400, detail="Booking is already Paid")
            
            # changed the status from booked to paid
            r["status"] = "Paid"
            
            #for creating the transaction record
            new_tx_id = max([t["id"] for t in transactions], default=0) + 1
            new_transaction = {
                "id": new_tx_id,
                "service_category": "Studio Rental",
                "reference_id": r["id"],
                "client_name": r["client_name"],
                "date": str(date.today()),
                "payment_method": payment.payment_method,
                "amount_paid": r["total_fee"],
                "status": "Completed"
            }
            transactions.append(new_transaction)
            save_data(data)
            return r
    raise HTTPException(status_code=404, detail="Booking ID not found")


# --- 4. UPDATE: Modify an existing Studio Booking (PUT) ---
@app.put("/studio-rentals/{rental_id}", status_code=200)
def update_studio_rental(rental_id: int, updated_data: StudioRentalInput): # flow: kukunin ung rental id and ung updated data json from main.py
    data = load_data()
    rentals = data["studio_rentals"]
    hourly_rate = data["settings"]["studio_hourly_rate"]
    
    # looping to check if the data is already paid
    for r in rentals:
        if r["id"] == rental_id:
            # Preventing paid transactions to be edited
            if r["status"] == "Paid":
                raise HTTPException(status_code=400, detail="Cannot update a booking that is already Paid")
            
            # if hindi naman paid proceed lng
            r["client_name"] = updated_data.client_name
            r["contact_number"] = updated_data.contact_number
            r["date"] = updated_data.date
            r["start_time"] = updated_data.start_time
            r["hours"] = updated_data.hours
            r["total_fee"] = hourly_rate * updated_data.hours
            
            save_data(data)
            return r # return r para makita sa postman na working (didisplay ung piniling id na updated)
        
    raise HTTPException(status_code=404, detail="Booking ID not FOUND") # didisplay sa postman
            
            
# - - - - - - - - - - - - - - Studio Rental API - - - - - - - - - - - - - -  #         