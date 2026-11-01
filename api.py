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
        
def get_next_id(items):
    return max([item["id"] for item in items], default=0) + 1


def record_transaction(data, category, ref_id, client_name, amount, payment_method):
    transactions = data["transactions"] # opens the json with the class transactions
    new_id = get_next_id(transactions)

    new_tx = {
        "id": new_id,
        "service_category": category,
        "reference_id": ref_id,
        "client_name": client_name,
        "date": str(date.today()),
        "payment_method": payment_method,
        "amount_paid": amount,
        "status": "Completed"
    }
    transactions.append(new_tx)


# - - - - - - - - - - - - - - Studio Rental API - - - - - - - - - - - - - -  #         

# --- 1. (GET) ---
@app.get("/studio-rentals", status_code=200)
def get_studio_rentals():
    data = load_data()
    return data["studio_rentals"] # eto ung ilalagay sa terminal\
        # studio_rentals come's from the json data title



# --- 2. (POST) ---
@app.post("/studio-rentals", status_code=201)
def create_studio_rental(booking: StudioRentalInput): # base on the modeled created
    #the booking is from the new_booking inside the main.py
    data = load_data() # load the data from data.json
    rentals = data["studio_rentals"] #this is where it will get stored

    # Get the hourly rate from settings
    hourly_rate = data["settings"]["studio_hourly_rate"] # from the data.json and settings and hourly rate data

    # Auto-increment ID
    new_id = get_next_id(rentals)
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


# --- 3. (PATCH) ---
@app.patch("/studio-rentals/{rental_id}/pay", status_code=200)
def pay_studio_rental(rental_id: int, payment: ConfirmPaymentInput):
    data = load_data()
    rentals = data["studio_rentals"]
    
    # for finding the id
    for r in rentals:
        if r["id"] == rental_id:
            if r["status"] == "Paid":
                raise HTTPException(status_code=400, detail="Booking is already Paid")
            
            # changed the status from booked to paid
            r["status"] = "Paid"
            
            #for creating the transaction record
            
            # data for getting the json file into the function 
            # Studio Rental is the Category from the json file
            # gets the id of the current rental
            # gets the name of the current rental
            # gets the payment then uses the model.py to get the payment_method
            record_transaction(data, "Studio Rental", r["id"], r["client_name"], r["total_fee"], payment.payment_method)
            
            save_data(data)
            return r
    raise HTTPException(status_code=404, detail="Booking ID not found")


# --- 4. (PUT) ---
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
            
            
# --- 5. (DELETE) ---
@app.delete("/studio-rentals/{rental_id}", status_code=200)
def delete_studio_rental(rental_id: int): # rental id ng nilagay ng user
    data = load_data()
    rentals = data["studio_rentals"] # rentals naman ung mismong json data

    # looping to find the booking by ID
    for r in rentals:
        if r["id"] == rental_id:
            # Preventing paid transactions from being deleted
            if r["status"] == "Paid":
                raise HTTPException(status_code=400, detail="Cannot delete a booking that is already Paid")

            # if hindi paid, remove from the list
            rentals.remove(r)
            save_data(data)
            return r # returns the deleted booking so CLI/Postman can show what was removed

    raise HTTPException(status_code=404, detail="Booking ID not found")



# - - - - - - - - - - - - - - Transactions API - - - - - - - - - - - - - -  #

# --- 1. (GET) Get all Transactions ---
@app.get("/transactions", status_code=200)
def get_transactions():
    data = load_data()
    return data["transactions"] # kinukuha ung lahat ng payment records sa data.json


# --- 2. (PATCH) Update Payment Method of a Transaction ---
@app.patch("/transactions/{tx_id}", status_code=200)
def update_transaction_payment(tx_id: int, payment: ConfirmPaymentInput): # tx_id ung piniling transaction ID, payment ung Cash or E-Wallet
    data = load_data()
    transactions = data["transactions"]

    # looping to find the transaction by ID
    for t in transactions:
        if t["id"] == tx_id:
            # pinapalitan ung payment_method (Cash <-> E-Wallet)
            t["payment_method"] = payment.payment_method
            save_data(data)
            return t # ibabalik ung updated transaction para madisplay sa table

    raise HTTPException(status_code=404, detail="Transaction ID not found")
