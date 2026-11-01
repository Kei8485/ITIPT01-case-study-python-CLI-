import json
from fastapi import FastAPI, HTTPException
from models import StudioRentalInput, LuthieryInput, LuthieryStatusInput, ConfirmPaymentInput # ung asa models ko
from datetime import date


# 13 API's 

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

# Created this because 2 references will use this 
# this only records the transanction. Pushes it to the transactions json file
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

# --- 1. (GET) Get all Studio Bookings (with optional ?status= filter) ---
@app.get("/studio-rentals", status_code=200)
def get_studio_rentals(status: str | None = None):
    data = load_data()
    rentals = data["studio_rentals"] # eto ung ilalagay sa terminal
        # studio_rentals come's from the json data title

    # if may piniling status filter (Booked or Paid), sasalain lang ung nagtutugma
    if status:
        return [r for r in rentals if r["status"].lower() == status.lower()]

    return rentals



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



# - - - - - - - - - - - - - - Luthiery Services API - - - - - - - - - - - - - -  #

# --- 1. (GET) Get all Luthiery Repair Jobs (with optional ?status= filter) ---
@app.get("/luthiery", status_code=200)
def get_luthiery_services(status: str | None = None):
    data = load_data() # the [] creates a empty list for the luthiery services if it still doesnt exist
    repairs = data.get("luthiery_services", []) # kinukuha ung lahat ng repair jobs sa data.json

    # if may piniling status filter (Pending, In Progress, or Completed), 
    if status:
        #gives the filtered data dpending what the status is then compare it to return the filtered data
        return [r for r in repairs if r["status"].lower() == status.lower()]
    # gives the unfiltered data
    return repairs


# --- 2. (POST) Add New Luthiery Repair Job ---
@app.post("/luthiery", status_code=201)
def create_luthiery_service(job: LuthieryInput): # base sa LuthieryInput model sa models.py
    data = load_data()
    if "luthiery_services" not in data:
        data["luthiery_services"] = []
    repairs = data["luthiery_services"]

    # Auto-increment ID
    new_id = get_next_id(repairs)

    new_job = {
        "id": new_id,
        "client_name": job.client_name,
        "contact_number": job.contact_number,
        "date_issued": str(date.today()),
        "instrument_type": job.instrument_type,
        "issue_description": job.issue_description,
        "estimated_cost": job.estimated_cost,
        "status": "Pending" # default status pag bagong tanggap ung gitara
    }

    repairs.append(new_job)
    save_data(data)
    return new_job


# --- 3a. (PATCH) Update Repair Status (Pending <-> In Progress) ---
@app.patch("/luthiery/{job_id}/status", status_code=200)
def update_luthiery_status(job_id: int, status_input: LuthieryStatusInput):
    data = load_data()
    repairs = data.get("luthiery_services", [])

    for j in repairs:
        if j["id"] == job_id:
            if j["status"] == "Completed":
                raise HTTPException(status_code=400, detail="Repair job is already Completed and Paid")

            # pinapalitan ung status (halimbawa: Pending -> In Progress)
            j["status"] = status_input.status
            save_data(data)
            return j

    raise HTTPException(status_code=404, detail="Repair Job ID not found")


# --- 3b. (PATCH) Complete Repair & Confirm Payment ---
@app.patch("/luthiery/{job_id}/pay", status_code=200)
def pay_luthiery_service(job_id: int, payment: ConfirmPaymentInput):
    data = load_data()
    repairs = data.get("luthiery_services", [])

    # hinahanap ung repair job gamit ung ID
    for r in repairs:
        if r["id"] == job_id:
            if r["status"] == "Completed":
                raise HTTPException(status_code=400, detail="Repair job is already Completed and Paid")

            # gagawing Completed ung status at gagawa ng transaction record
            r["status"] = "Completed"
            record_transaction(data, "Luthiery Service", r["id"], r["client_name"], r["estimated_cost"], payment.payment_method)

            save_data(data)
            return r

    raise HTTPException(status_code=404, detail="Repair Job ID not found")


# --- 4. (PUT) Update Luthiery Repair Job Details ---
@app.put("/luthiery/{job_id}", status_code=200)
def update_luthiery_service(job_id: int, updated_data: LuthieryInput): # kukunin ung job_id at ung bagong details galing sa main.py
    data = load_data()
    repairs = data.get("luthiery_services", [])

    for j in repairs:
        if j["id"] == job_id:
            # bawal na i-edit pag Completed / bayad na
            if j["status"] == "Completed":
                raise HTTPException(status_code=400, detail="Cannot update a repair job that is already Completed")

            j["client_name"] = updated_data.client_name
            j["contact_number"] = updated_data.contact_number
            j["instrument_type"] = updated_data.instrument_type
            j["issue_description"] = updated_data.issue_description
            j["estimated_cost"] = updated_data.estimated_cost

            save_data(data)
            return j

    raise HTTPException(status_code=404, detail="Repair Job ID not found")


# --- 5. (DELETE) Delete / Cancel Luthiery Repair Job ---
@app.delete("/luthiery/{job_id}", status_code=200)
def delete_luthiery_service(job_id: int):
    data = load_data()
    repairs = data.get("luthiery_services", [])

    for j in repairs:
        if j["id"] == job_id:
            # bawal burahin pag Completed / bayad na
            if j["status"] == "Completed":
                raise HTTPException(status_code=400, detail="Cannot delete a repair job that is already Completed")

            repairs.remove(j)
            save_data(data)
            return j

    raise HTTPException(status_code=404, detail="Repair Job ID not found")



# - - - - - - - - - - - - - - Transactions API - - - - - - - - - - - - - -  #

# --- 1. (GET) Get all Transactions (with optional ?payment_method= filter) ---
@app.get("/transactions", status_code=200)
def get_transactions(payment_method: str | None = None):
    data = load_data()
    transactions = data["transactions"] # kinukuha ung lahat ng payment records sa data.json

    # if may piniling filter (Cash or E-Wallet), sasalain lang ung nagtutugma
    if payment_method:
        return [t for t in transactions if t["payment_method"].lower() == payment_method.lower()]

    return transactions


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
