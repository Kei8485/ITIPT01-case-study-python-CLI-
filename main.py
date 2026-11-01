import re
import requests
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from utils import *

#Main Menu
def mainMenu():
    clear_screen()
    # Header Banner
    print(Panel.fit(
        "[bold cyan]🎸 LA SCHOOL OF ROCK[/bold cyan]\n"
        "[dim red]Cabanatuan City, Nueva Ecija — Internal System[/dim red]",
        border_style="red"
    ))
    
    # Menu Options
    print("[bold yellow]Select a Module:[/bold yellow]")
    print("[bold green][1][/bold green] [dark_red]Studio Rentals (Band Rehearsals & Recording)[/dark_red]")
    print("[bold green][2][/bold green] [dark_red]Luthiery Services (Guitar Repairs & Mods)[/dark_red]")
    print("[bold green][3][/bold green] [dark_red]Transactions & Payment Records[/dark_red]")
    print("[bold red][0][/bold red] Exit System\n")
    
    choice = Prompt.ask("[dim red]Enter option [0-3][/dim red]").strip()
    return choice

# View studio bookings (with optional status filter & summary)
def viewStudioRentals(filter_status=None):
    # tatawag sa API, if may filter_status (Booked/Paid), ipapasa as query parameter ?status=...
    url = f"/studio-rentals?status={filter_status}" if filter_status else "/studio-rentals"
    response = api_get(url) # uses the function from utils
    # stores the json list 
    
    if response is None: 
        return # if None that means server error
    
    if not response:
        msg = f"[yellow]No '{filter_status}' studio bookings found![/yellow]" if filter_status else "[yellow]No studio bookings found in the system yet![/yellow]"
        print(msg)
        pauseDisplay()
        clear_screen()
        return

    title = f"🎸 {filter_status} Studio Bookings" if filter_status else "🎸 All Studio Bookings"
    # shows the tables
    showTable(response, title, STUDIO_COLUMNS)

    # Kukuwentahin ung summary ng studio bookings
    total_fee = sum(r["total_fee"] for r in response)
    booked_total = sum(r["total_fee"] for r in response if r["status"].lower() == "booked")
    paid_total = sum(r["total_fee"] for r in response if r["status"].lower() == "paid")

    if filter_status:
        summary_text = f"[bold white]Total {filter_status} Amount:[/bold white] [bold green]₱{total_fee:,.2f}[/bold green] ({len(response)} booking/s)"
    else:
        summary_text = (
            f"[bold yellow]Unpaid (Booked):[/bold yellow] [bold yellow]₱{booked_total:,.2f}[/bold yellow]   |   "
            f"[bold green]Paid:[/bold green] [bold green]₱{paid_total:,.2f}[/bold green]   |   "
            f"[bold white]Total:[/bold white] [bold cyan]₱{total_fee:,.2f}[/bold cyan] ({len(response)} booking/s)"
        )

    print(Panel(summary_text, title="[bold]Studio Bookings Summary[/bold]", border_style="cyan", expand=False))

    pauseDisplay()
    clear_screen()


# Submenu para makapili kung All, Booked only, or Paid only sa Studio Rentals
def viewStudioRentalsMenu():
    while True:
        clear_screen()
        print(Panel.fit(
            "[bold aquamarine1]🔍 VIEW & FILTER STUDIO BOOKINGS[/bold aquamarine1]\n"
            "[dim]Filter studio reservations by status[/dim]",
            border_style="cyan"
        ))
        print("[bold yellow]Select Filter:[/bold yellow]")
        print("[bold green][1][/bold green] View All Studio Bookings")
        print("[bold green][2][/bold green] Booked (Unpaid / Upcoming) Only")
        print("[bold green][3][/bold green] Paid (Completed) Only")
        print("[bold red][0][/bold red] Back\n")

        choice = Prompt.ask("[dim red]Enter option [0-3][/dim red]").strip()
        match choice:
            case "1":
                clear_screen()
                viewStudioRentals()
            case "2":
                clear_screen()
                viewStudioRentals(filter_status="Booked")
            case "3":
                clear_screen()
                viewStudioRentals(filter_status="Paid")
            case "0":
                clear_screen()
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 3.[/bold red]\n")
    
# Add new Studio Booking
def addStudioBooking():
    
    while True:
        # To check if it can connect to the server
        get_response = api_get("/studio-rentals")
        
        if get_response is None:
            return
        
        
        showHeadingPanel("➕ ADD NEW STUDIO BOOKING", "000=keep current | 00=back | 0=cancel")
        
        new_booking = step_by_step_edit(STUDIO_QUESTIONS) # ask the questions and make the user input it
        if not new_booking:
            return  # cancel and return to menu
        
        if not ask_confirm(f"Add new reservation for {new_booking['client_name']} on {new_booking['date']} at {new_booking['start_time']}?"): # ask confirmation
            clear_screen()
            print("[cyan]Booking cancelled...[/cyan]\n")
            return
        
        response = api_post("/studio-rentals",new_booking)
        if response is None:
            return    
            
        # if its successful it will proceed here and it will return the r as the json file
        # we show that the data that was sent was a success
        showTable(response,"✅ New Studio Booking Added", STUDIO_COLUMNS)
        # pag nilagay ko new_booking hindi sya completo
        # so need ko ung response para makuha ung legit data na kompleto
        pauseDisplay()
        clear_screen()
        return

#Update Status for finished studio booking
def finishStudioBooking():
    while True:
        response = api_get("/studio-rentals")
        if response is None:
            return
        
        booked_rentals = [r for r in response if r["status"] == "Booked"] # may r sa unahan para makuha ung lahat ng data
        showHeadingPanel("➕ Unpaid Studio Bookings", "Choose The Clients That Has Paid")
        if not booked_rentals:# pag alang laman ung booked rentals
            print("[yellow]No unpaid 'Booked' studio reservations found![/yellow]")
            pauseDisplay()
            clear_screen()
            return
        
        # if merong laman ung booked rentals shows the table
        showTable(booked_rentals, "🎸 Unpaid Clients Bookings", STUDIO_COLUMNS)
        
        # looks only at the ID that has booked status
        valid_ids = [str(r["id"]) for r in booked_rentals]
        
        while True:
            while True:
                chosen_id = ask_input("Choose the ID of the Client to Confirm the Payment", r"^[1-9]\d*$", "ID must be a valid number!")
                if not chosen_id: return
                if chosen_id in valid_ids: # compare the chosen id to the valid id (valid id ung mga Booked)
                    break
                #prints this if its not in valid ids
                print(f"[bold red]❌ Booking ID #{chosen_id} is not in the unpaid list above! Choose from: {', '.join(valid_ids)}[/bold red]")
            
            # Ask for Payment Method (1 = Cash, 2 = E-Wallet)
            print("\n[bold yellow]Select Payment Method:[/bold yellow]")
            print("[bold green][1][/bold green] Cash")
            print("[bold green][2][/bold green] E-Wallet")
            
            pay_choice = ask_input("Enter choice [1-2] (or 00 to go back)", r"^(1|2|00)$", "Please enter 1 for Cash, 2 for E-Wallet, or 00 to go back!")
            if pay_choice is None: return
            if pay_choice == "00":
                print("[yellow]↩️ Going back to choose Booking ID...[/yellow]\n")
                continue # goes back to choosing Booking ID!
                
            payment_method = "Cash" if pay_choice == "1" else "E-Wallet"
            break
        
        # Grab chosen booking to display fee & name in confirmation
        target = next(r for r in booked_rentals if str(r["id"]) == chosen_id) # finds the chosen ID so it can get the client_name
        # Ask for confirmation before charging
        if not ask_confirm(f"Confirm payment of ₱{target['total_fee']:,.2f} for {target['client_name']} via {payment_method}?"):
            clear_screen()
            print("[cyan]Payment cancelled...[/cyan]\n")
            return
        
        updatedData = api_patch(f"/studio-rentals/{chosen_id}/pay", {"payment_method": payment_method})
        
        if updatedData is None: # if validation are not valid
            return
        
        # prints if this if success
        print(f"\n[bold green]✅ Payment Confirmed! Booking #{updatedData['id']} ({updatedData['client_name']}) is now PAID via {payment_method}![/bold green]")
        print("[dim green]Transaction record has been automatically created and saved to data.json.\n[/dim green]")
            
        showTable(updatedData, "✅ Updated Studio Booking", STUDIO_COLUMNS)
            
        pauseDisplay()
        clear_screen()
        return
        
# Updating all details for Put API
def udpateStudioBooking():
    while True:
        # vvvvvvv SHOWING OF TABLES PALANG vvvvvvv #
        
        response = api_get("/studio-rentals")
        
        if response is None:
            return
        
        
        #showing booked rentals only and not yet paid
        booked_rentals = [r for r in response if r ["status"] == "Booked"] # lalagay na dito ung data
        # MAIN JOB ^^^^^^ for showing the filtered data
        
        # if empty
        if not booked_rentals:
            print("[yellow]No editable 'Booked' studio reservations found![/yellow]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            clear_screen()
            return
        
        ##display if all is valid
        # Display table of editable bookings
        showTable(booked_rentals,"📝 Editable Studio Bookings (Status: Booked)", STUDIO_COLUMNS)
        print("[red](<Type 0 at any time to cancel and go back>)\n")    
            
        valid_ids = [str(r["id"]) for r in booked_rentals]
        #MAIN JOB ^^^ Since ung isa ay pang display, this ensure validation (gets the valid ids the user can only select)
        #str(r["id"]) - to make sure id lng ang makukuha 
        
        while True: # need itong loop para icheck kung ung ID ay asa choices of data
            rental_id = ask_input("Enter Booking ID to Update", r"^[1-9]\d*$", "ID must be a valid number!")
            if not rental_id: return 
            if rental_id in valid_ids:
                break
            print(f"[bold red]❌ Booking ID #{rental_id} is not in the list above! Choose from: {', '.join(valid_ids)}[/bold red]")
            
        # ^^^^^^^ SHOWING OF TABLES PALANG ^^^^^^^ #
            
            
        # vvvvvvv SHOWING SELECTED ITEM TO EDIT vvvvvvv #    
        #  Grab the current booking object so we know its existing details
        selected_booking = next(r for r in booked_rentals if str(r["id"]) == rental_id)
        # Shows the current item that is being edited
        clear_screen()
        showHeadingPanel(f"✏️ EDITING BOOKING #{rental_id}", "000=keep current | 00=back | 0=cancel")
        
        # Ask the information that will be updated
                # Print the current details table
        showTable(selected_booking,f"📋 Current Details for Booking #{rental_id}", STUDIO_COLUMNS)
        
        # does the input function for PUT
        updated_information = step_by_step_edit(STUDIO_QUESTIONS, selected_booking)
        
        if updated_information is None:
            # none lng sya pag nag back ung user [0]
            return
        
        # Ask for confirmation before saving changes
        if not ask_confirm(f"Save updated changes for Booking #{rental_id}?"):
            clear_screen()
            print("[cyan]Update cancelled...[/cyan]\n")
            return
            
        # doing the PUT API Request
        response = api_put(f"/studio-rentals/{rental_id}",updated_information)
        
        if response is None:
            return
        
        showTable(response, f"✅ Booking #{rental_id} successfully updated!",STUDIO_COLUMNS)

            
        pauseDisplay()
        return
    
# Cancel / Delete a Studio Booking (DELETE)
def deleteStudioBooking():
    while True:
        response = api_get("/studio-rentals")
        if response is None:
            return
        
        # showing booked rentals only (cannot delete already paid bookings)
        booked_rentals = [r for r in response if r["status"] == "Booked"]
        showHeadingPanel("🗑️ CANCEL STUDIO BOOKING", "Select a reservation to cancel / delete")
        
        if not booked_rentals:
            print("[yellow]No cancellable 'Booked' studio reservations found![/yellow]")
            pauseDisplay()
            clear_screen()
            return
            
        showTable(booked_rentals, "🎸 Cancellable Studio Bookings", STUDIO_COLUMNS)
        
        # validate chosen ID
        valid_ids = [str(r["id"]) for r in booked_rentals]
        while True:
            chosen_id = ask_input("Enter Booking ID to Cancel", r"^[1-9]\d*$", "ID must be a valid number!")
            if not chosen_id: return
            if chosen_id in valid_ids:
                break
            print(f"[bold red]❌ Booking ID #{chosen_id} is not in the list above! Choose from: {', '.join(valid_ids)}[/bold red]")
            
        # grab the booking so we can show client name in confirmation
        selected_booking = next(r for r in booked_rentals if str(r["id"]) == chosen_id)
        
        # Ask for confirmation before permanently deleting!
        if not ask_confirm(f"Are you sure you want to permanently cancel Booking #{chosen_id} for {selected_booking['client_name']}?"):
            clear_screen()
            print("[cyan]Deletion cancelled...[/cyan]\n")
            return
            
        # call DELETE API
        deleted = api_delete(f"/studio-rentals/{chosen_id}")
        if deleted is None:
            return
            
        print(f"\n[bold green]✅ Booking #{chosen_id} successfully cancelled and deleted![/bold green]\n")
        showTable(deleted, "🗑️ Deleted Studio Booking", STUDIO_COLUMNS)
        
        pauseDisplay()
        clear_screen()
        return
   
#Studio Rental
def studioRental():
    clear_screen()
    while True:
        print(Panel.fit(
            "[bold aquamarine1]🎸 STUDIO RENTALS MODULE[/bold aquamarine1]\n"
            "[dim red]Band Rehearsals & Recording Reservations[/dim red]",
            border_style="cyan"
        ))

        print("[bold yellow]Select an Action:[/bold yellow]")
        print("[bold green][1][/bold green] [dark_red]View & Filter Studio Bookings (All / Booked / Paid)[/dark_red]")
        print("[bold green][2][/bold green] [dark_red]Add New Studio Booking[/dark_red]")
        print("[bold green][3][/bold green] [dark_red]Finish Booking & Confirm Payment[/dark_red]")
        print("[bold green][4][/bold green] [dark_red]Update Booking Details[/dark_red]")
        print("[bold green][5][/bold green] [dark_red]Delete / Cancel Booking[/dark_red]")
        print("[bold red][0][/bold red] Back to Main Menu\n")

        choice = Prompt.ask("[dim red]Enter option [0-5][/dim red]").strip()
        match choice:
            case "1":
                # show & filter studio bookings
                viewStudioRentalsMenu() 
            case "2":
                # add new studio bookings
                clear_screen()
                print("[cyan]Adding new studio booking...[/cyan]\n")
                addStudioBooking()
            case "3":
                # display finished booking and payment
                clear_screen()
                print("[cyan]Finishing booking & confirming payment...[/cyan]\n")
                finishStudioBooking()
            case "4":
                # update studio bookings
                clear_screen()
                print("[cyan]Updating booking details...[/cyan]\n")
                udpateStudioBooking()
            case "5":
                # delete studio bookings
                clear_screen()
                print("[cyan]Deleting studio booking...[/cyan]\n")
                deleteStudioBooking()
            case "0":
                print("[yellow]Returning to Main Menu...[/yellow]\n")
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 5.[/bold red]\n")


# - - - - - - - - - Luthiery Services Module - - - - - - - - -

# View luthiery repair jobs (with optional status filter & summary)
def viewLuthieryServices(filter_status=None):
    # tatawag sa API, if may filter_status (Pending/In Progress/Completed), ipapasa as query parameter ?status=...
    url = f"/luthiery?status={filter_status}" if filter_status else "/luthiery"
    # '?' is a divider and used for filtering 
    # the one we put for the filter status is the one we will use to compare the filter depending in our logic in the api
    response = api_get(url) # kumukuha ng repair jobs galing sa API
    
    if response is None:
        return # if None that means server error
        
    if not response: # pag alang laman ung luthiery_services list
        msg = f"[yellow]No '{filter_status}' luthiery repair jobs found![/yellow]" if filter_status else "[yellow]No luthiery repair jobs found in the system yet![/yellow]"
        print(msg)
        pauseDisplay()
        clear_screen()
        return
        
    title = f"🔧 {filter_status} Luthiery Repair Jobs" if filter_status else "🔧 All Luthiery Repair & Modification Jobs"
    # ipapakita ung table gamit ung LUTHIERY_COLUMNS blueprint
    showTable(response, title, LUTHIERY_COLUMNS)

    # kukunin ung summary ng luthiery repair jobs
    total_cost = sum(r["estimated_cost"] for r in response)
    pending_cost = sum(r["estimated_cost"] for r in response if r["status"].lower() == "pending")
    inprogress_cost = sum(r["estimated_cost"] for r in response if r["status"].lower() == "in progress")
    completed_cost = sum(r["estimated_cost"] for r in response if r["status"].lower() == "completed")

    if filter_status:
        summary_text = f"[bold white]Total {filter_status} Cost:[/bold white] [bold green]₱{total_cost:,.2f}[/bold green] ({len(response)} repair job/s)"
    else:
        summary_text = (
            f"[bold yellow]Pending:[/bold yellow] ₱{pending_cost:,.2f}   |   "
            f"[bold cyan]In Progress:[/bold cyan] ₱{inprogress_cost:,.2f}   |   "
            f"[bold green]Completed (Paid):[/bold green] ₱{completed_cost:,.2f}   |   "
            f"[bold white]Total:[/bold white] [bold yellow]₱{total_cost:,.2f}[/bold yellow] ({len(response)} job/s)"
        )

    print(Panel(summary_text, title="[bold]Luthiery Repairs Summary[/bold]", border_style="cyan", expand=False))

    pauseDisplay()
    clear_screen()


# Submenu para makapili kung All, Pending, In Progress, or Completed sa Luthiery Services
def viewLuthieryMenu():
    while True:
        clear_screen()
        print(Panel.fit(
            "[bold aquamarine1]🔍 VIEW & FILTER REPAIR JOBS[/bold aquamarine1]\n"
            "[dim]Filter guitar & instrument repairs by status[/dim]",
            border_style="cyan"
        ))
        print("[bold yellow]Select Filter:[/bold yellow]")
        print("[bold green][1][/bold green] View All Repair Jobs")
        print("[bold green][2][/bold green] Pending Repairs Only")
        print("[bold green][3][/bold green] In Progress Repairs Only")
        print("[bold green][4][/bold green] Completed (Paid) Repairs Only")
        print("[bold red][0][/bold red] Back\n")

        choice = Prompt.ask("[dim red]Enter option [0-4][/dim red]").strip()
        match choice:
            case "1":
                clear_screen()
                viewLuthieryServices()
            case "2":
                clear_screen()
                viewLuthieryServices(filter_status="Pending")
            case "3":
                clear_screen()
                viewLuthieryServices(filter_status="In Progress")
            case "4":
                clear_screen()
                viewLuthieryServices(filter_status="Completed")
            case "0":
                clear_screen()
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 4.[/bold red]\n")


# Add new Luthiery Repair Job (POST /luthiery)
def addLuthieryJob():
    while True:
        # check muna kung connected sa server
        get_response = api_get("/luthiery")
        if get_response is None:
            return
            
        showHeadingPanel("➕ ADD NEW REPAIR / MODIFICATION JOB", "000=keep current | 00=back | 0=cancel")
        
        new_job = step_by_step_edit(LUTHIERY_QUESTIONS) # tatanungin ung user base sa LUTHIERY_QUESTIONS
        if not new_job:
            return # cancel at babalik sa menu
            
        if not ask_confirm(f"Add new repair job for {new_job['client_name']} ({new_job['instrument_type']}) costing ₱{new_job['estimated_cost']:,.2f}?"):
            clear_screen()
            print("[cyan]Repair job creation cancelled...[/cyan]\n")
            return
            
        response = api_post("/luthiery", new_job)
        if response is None:
            return
            
        # ipapakita ung bagong gawang repair job kasama ung auto-generated ID at status
        showTable(response, "✅ New Luthiery Repair Job Added", LUTHIERY_COLUMNS)
        pauseDisplay()
        clear_screen()
        return


# Update Repair Progress (Pending <-> In Progress) OR Complete & Pay (PATCH)
def finishLuthieryJob():
    while True:
        response = api_get("/luthiery")
        if response is None:
            return
            
        # kukunin lang ung mga ongoing repairs (Pending or In Progress) na hindi pa Completed
        active_jobs = [j for j in response if j["status"] != "Completed"]
        showHeadingPanel("🔧 UPDATE REPAIR STATUS / CONFIRM PAYMENT", "Select an ongoing repair job to update status or complete payment")
        
        if not active_jobs: # pag lahat ay Completed na o walang laman
            print("[yellow]No ongoing ('Pending' or 'In Progress') repair jobs found![/yellow]")
            pauseDisplay()
            clear_screen()
            return
            
        showTable(active_jobs, "🔧 Ongoing Luthiery Repair Jobs", LUTHIERY_COLUMNS)
        
        valid_ids = [str(j["id"]) for j in active_jobs]
        
        while True:
            while True:
                chosen_id = ask_input("Choose the Repair Job ID", r"^[1-9]\d*$", "ID must be a valid number!")
                if not chosen_id: return
                if chosen_id in valid_ids: # ichecheck kung nasa active list ung ID
                    break
                print(f"[bold red]❌ Repair Job ID #{chosen_id} is not in the ongoing list above! Choose from: {', '.join(valid_ids)}[/bold red]")
                
            target = next(j for j in active_jobs if str(j["id"]) == chosen_id)
            print(f"\n[blue]Selected Job #{chosen_id}: {target['client_name']} ({target['instrument_type']}) — Current Status: [bold yellow]{target['status']}[/bold yellow]")
            
            # Papipiliin kung gagawing In Progress/Pending o kung tapos na at magbabayad na (Completed)
            toggle_status = "In Progress" if target["status"] == "Pending" else "Pending"
            print("\n[bold yellow]Select Action:[/bold yellow]")
            print(f"[bold green][1][/bold green] Change Status to '[bold cyan]{toggle_status}[/bold cyan]' (No payment yet)")
            print("[bold green][2][/bold green] Mark as '[bold green]Completed[/bold green]' & Confirm Payment")
            
            action_choice = ask_input("Enter choice [1-2] (or 00 to go back)", r"^(1|2|00)$", "Please enter 1, 2, or 00 to go back!")
            if action_choice is None: return
            if action_choice == "00":
                print("[yellow]↩️ Going back to choose Repair Job ID...[/yellow]\n")
                continue
                
            # Option 1: Palitan lang ung status (Pending <-> In Progress)
            if action_choice == "1":
                if not ask_confirm(f"Update Job #{chosen_id} ({target['client_name']}) status from '{target['status']}' to '{toggle_status}'?"):
                    clear_screen()
                    print("[cyan]Status update cancelled...[/cyan]\n")
                    return
                    
                updated_job = api_patch(f"/luthiery/{chosen_id}/status", {"status": toggle_status})
                if updated_job is None:
                    return
                    
                print(f"\n[bold green]✅ Repair Job #{chosen_id} status updated to {toggle_status}![/bold green]\n")
                showTable(updated_job, "✅ Updated Repair Job", LUTHIERY_COLUMNS)
                pauseDisplay()
                clear_screen()
                return
                
            # Option 2: Tapos na ung gawa at magbabayad na ung client (Completed + Transaction record)
            print("\n[bold yellow]Select Payment Method:[/bold yellow]")
            print("[bold green][1][/bold green] Cash")
            print("[bold green][2][/bold green] E-Wallet")
            
            pay_choice = ask_input("Enter choice [1-2] (or 00 to go back)", r"^(1|2|00)$", "Please enter 1 for Cash, 2 for E-Wallet, or 00 to go back!")
            if pay_choice is None: return
            if pay_choice == "00":
                print("[yellow]↩️ Going back to choose Repair Job ID...[/yellow]\n")
                continue
                
            payment_method = "Cash" if pay_choice == "1" else "E-Wallet"
            break
            
        if not ask_confirm(f"Confirm payment of ₱{target['estimated_cost']:,.2f} for {target['client_name']} ({target['instrument_type']}) via {payment_method}?"):
            clear_screen()
            print("[cyan]Payment cancelled...[/cyan]\n")
            return
            
        updated_job = api_patch(f"/luthiery/{chosen_id}/pay", {"payment_method": payment_method})
        if updated_job is None:
            return
            
        print(f"\n[bold green]✅ Payment Confirmed! Repair Job #{updated_job['id']} ({updated_job['client_name']}) is now COMPLETED via {payment_method}![/bold green]")
        print("[dim green]Transaction record has been automatically created and saved to data.json.\n[/dim green]")
        
        showTable(updated_job, "✅ Completed Repair Job", LUTHIERY_COLUMNS)
        pauseDisplay()
        clear_screen()
        return


# Update Luthiery Repair Job Details (PUT /luthiery/{job_id})
def updateLuthieryJob():
    while True:
        response = api_get("/luthiery")
        if response is None:
            return
            
        # ipapakita lang ung mga hindi pa Completed (bawal na i-edit pag bayad/tapos na)
        editable_jobs = [j for j in response if j["status"] != "Completed"]
        
        if not editable_jobs:
            print("[yellow]No editable ('Pending' or 'In Progress') repair jobs found![/yellow]")
            pauseDisplay()
            clear_screen()
            return
            
        showTable(editable_jobs, "📝 Editable Luthiery Repair Jobs", LUTHIERY_COLUMNS)
        print("[red](<Type 0 at any time to cancel and go back>)\n")
        
        valid_ids = [str(j["id"]) for j in editable_jobs]
        
        while True:
            job_id = ask_input("Enter Repair Job ID to Update", r"^[1-9]\d*$", "ID must be a valid number!")
            if not job_id: return
            if job_id in valid_ids:
                break
            print(f"[bold red]❌ Repair Job ID #{job_id} is not in the list above! Choose from: {', '.join(valid_ids)}[/bold red]")
            
        # kukunin ung napiling repair job para madisplay ung current details nya
        selected_job = next(j for j in editable_jobs if str(j["id"]) == job_id)
        
        clear_screen()
        showHeadingPanel(f"✏️ EDITING REPAIR JOB #{job_id}", "000=keep current | 00=back | 0=cancel")
        showTable(selected_job, f"📋 Current Details for Repair Job #{job_id}", LUTHIERY_COLUMNS)
        
        updated_information = step_by_step_edit(LUTHIERY_QUESTIONS, selected_job)
        if updated_information is None:
            return
            
        if not ask_confirm(f"Save updated changes for Repair Job #{job_id}?"):
            clear_screen()
            print("[cyan]Update cancelled...[/cyan]\n")
            return
            
        response = api_put(f"/luthiery/{job_id}", updated_information)
        if response is None:
            return
            
        showTable(response, f"✅ Repair Job #{job_id} successfully updated!", LUTHIERY_COLUMNS)
        pauseDisplay()
        return


# Delete / Cancel a Luthiery Repair Job (DELETE /luthiery/{job_id})
def deleteLuthieryJob():
    while True:
        response = api_get("/luthiery")
        if response is None:
            return
            
        # hindi pwedeng burahin pag Completed/bayad na
        cancellable_jobs = [j for j in response if j["status"] != "Completed"]
        showHeadingPanel("🗑️ CANCEL REPAIR JOB", "Select an ongoing repair job to cancel / delete")
        
        if not cancellable_jobs:
            print("[yellow]No cancellable ('Pending' or 'In Progress') repair jobs found![/yellow]")
            pauseDisplay()
            clear_screen()
            return
            
        showTable(cancellable_jobs, "🔧 Cancellable Luthiery Repair Jobs", LUTHIERY_COLUMNS)
        
        valid_ids = [str(j["id"]) for j in cancellable_jobs]
        while True:
            chosen_id = ask_input("Enter Repair Job ID to Cancel", r"^[1-9]\d*$", "ID must be a valid number!")
            if not chosen_id: return
            if chosen_id in valid_ids:
                break
            print(f"[bold red]❌ Repair Job ID #{chosen_id} is not in the list above! Choose from: {', '.join(valid_ids)}[/bold red]")
            
        selected_job = next(j for j in cancellable_jobs if str(j["id"]) == chosen_id)
        
        if not ask_confirm(f"Are you sure you want to permanently cancel Repair Job #{chosen_id} for {selected_job['client_name']} ({selected_job['instrument_type']})?"):
            clear_screen()
            print("[cyan]Deletion cancelled...[/cyan]\n")
            return
            
        deleted = api_delete(f"/luthiery/{chosen_id}")
        if deleted is None:
            return
            
        print(f"\n[bold green]✅ Repair Job #{chosen_id} successfully cancelled and deleted![/bold green]\n")
        showTable(deleted, "🗑️ Deleted Repair Job", LUTHIERY_COLUMNS)
        
        pauseDisplay()
        clear_screen()
        return


# Luthiery Services Menu
def luthieryModule():
    clear_screen()
    while True:
        print(Panel.fit(
            "[bold aquamarine1]🔧 LUTHIERY SERVICES MODULE[/bold aquamarine1]\n"
            "[dim red]Guitar & Instrument Repairs and Modifications[/dim red]",
            border_style="cyan"
        ))

        print("[bold yellow]Select an Action:[/bold yellow]")
        print("[bold green][1][/bold green] [dark_red]View & Filter Repair Jobs (All / Pending / In Progress / Completed)[/dark_red]")
        print("[bold green][2][/bold green] [dark_red]Add New Repair Job[/dark_red]")
        print("[bold green][3][/bold green] [dark_red]Update Repair Status / Confirm Payment[/dark_red]")
        print("[bold green][4][/bold green] [dark_red]Update Repair Job Details[/dark_red]")
        print("[bold green][5][/bold green] [dark_red]Delete / Cancel Repair Job[/dark_red]")
        print("[bold red][0][/bold red] Back to Main Menu\n")

        choice = Prompt.ask("[dim red]Enter option [0-5][/dim red]").strip()
        match choice:
            case "1":
                viewLuthieryMenu()
            case "2":
                clear_screen()
                print("[cyan]Adding new repair job...[/cyan]\n")
                addLuthieryJob()
            case "3":
                clear_screen()
                print("[cyan]Updating repair status / confirming payment...[/cyan]\n")
                finishLuthieryJob()
            case "4":
                clear_screen()
                print("[cyan]Updating repair job details...[/cyan]\n")
                updateLuthieryJob()
            case "5":
                clear_screen()
                print("[cyan]Deleting repair job...[/cyan]\n")
                deleteLuthieryJob()
            case "0":
                print("[yellow]Returning to Main Menu...[/yellow]\n")
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 5.[/bold red]\n")


# - - - - - - - - - Transactions & Payment Records Module - - - - - - - - -

# View transactions (with filter & total summary)
def viewTransactions(filter_method=None):
    # tatawag sa API, if may filter_method (Cash/E-Wallet), ipapasa as query parameter ?payment_method=...
    url = f"/transactions?payment_method={filter_method}" if filter_method else "/transactions"
    transactions = api_get(url)
    
    if transactions is None:
        return # if None that means server error
        
    if not transactions: # pag walang nahanap na record
        msg = f"[yellow]No {filter_method} transactions found![/yellow]" if filter_method else "[yellow]No transaction records found in the system yet![/yellow]"
        print(msg)
        pauseDisplay()
        clear_screen()
        return
        
    title = f"💵 {filter_method} Transactions" if filter_method else "💵 All Transaction & Payment Records"
    
    # ipapakita ung table gamit ung TRANSACTION_COLUMNS blueprint
    showTable(transactions, title, TRANSACTION_COLUMNS)
    
    # Kukuwentahin ung total collection para sa listahan
    total_amount = sum(t["amount_paid"] for t in transactions)
    cash_total = sum(t["amount_paid"] for t in transactions if t["payment_method"].lower() == "cash")
    ewallet_total = sum(t["amount_paid"] for t in transactions if t["payment_method"].lower() == "e-wallet")
    
    # Summary Panel
    if filter_method:
        summary_text = f"[bold white]Total {filter_method} Collected:[/bold white] [bold green]₱{total_amount:,.2f}[/bold green] ({len(transactions)} transaction/s)"
    else:
        summary_text = (
            f"[bold magenta]Cash Total:[/bold magenta] [bold green]₱{cash_total:,.2f}[/bold green]   |   "
            f"[bold cyan]E-Wallet Total:[/bold cyan] [bold green]₱{ewallet_total:,.2f}[/bold green]   |   "
            f"[bold white]Grand Total:[/bold white] [bold yellow]₱{total_amount:,.2f}[/bold yellow] ({len(transactions)} total)"
        )
        
    print(Panel(summary_text, title="[bold]Summary[/bold]", border_style="green", expand=False))
    
    pauseDisplay()
    clear_screen()


# Submenu para makapili kung All, Cash only, or E-Wallet only
def viewTransactionsMenu():
    while True:
        clear_screen()
        print(Panel.fit(
            "[bold aquamarine1]🔍 VIEW & FILTER TRANSACTIONS[/bold aquamarine1]\n"
            "[dim]Filter transactions by payment method and view total collection[/dim]",
            border_style="cyan"
        ))
        print("[bold yellow]Select Filter:[/bold yellow]")
        print("[bold green][1][/bold green] View All (With Cash & E-Wallet Breakdown)")
        print("[bold green][2][/bold green] Cash Transactions Only")
        print("[bold green][3][/bold green] E-Wallet Transactions Only")
        print("[bold red][0][/bold red] Back\n")
        
        choice = Prompt.ask("[dim red]Enter option [0-3][/dim red]").strip()
        match choice:
            case "1":
                clear_screen()
                viewTransactions()
            case "2":
                clear_screen()
                viewTransactions(filter_method="Cash")
            case "3":
                clear_screen()
                viewTransactions(filter_method="E-Wallet")
            case "0":
                clear_screen()
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 3.[/bold red]\n")


# Update payment method of a transaction (PATCH /transactions/{tx_id})
def updateTransactionPayment():
    while True:
        response = api_get("/transactions")
        if response is None:
            return
            
        showHeadingPanel("✏️ UPDATE PAYMENT METHOD", "Switch a transaction between Cash and E-Wallet")
        
        if not response: # pag alang laman ung transactions
            print("[yellow]No transaction records found to update![/yellow]")
            pauseDisplay()
            clear_screen()
            return
            
        # ipapakita muna lahat ng transactions para makapili ng ID ung user
        showTable(response, "💵 All Transaction Records", TRANSACTION_COLUMNS)
        
        # kukunin lahat ng valid transaction IDs
        valid_ids = [str(t["id"]) for t in response]
        
        while True:
            while True:
                chosen_id = ask_input("Enter Transaction ID to Update Payment Method", r"^[1-9]\d*$", "ID must be a valid number!")
                if not chosen_id: return
                if chosen_id in valid_ids: # ichecheck kung ung piniling ID ay nasa listahan
                    break
                print(f"[bold red]❌ Transaction ID #{chosen_id} is not in the list above! Choose from: {', '.join(valid_ids)}[/bold red]")
                
            # hahanapin ung napiling transaction para makita kung ano ung current payment_method nya
            selected_tx = next(t for t in response if str(t["id"]) == chosen_id)
            print(f"\n[dim]Selected Transaction #{chosen_id} ({selected_tx['client_name']}) — Current Method:[/dim] [bold magenta]{selected_tx['payment_method']}[/bold magenta]")
            
            # Ask for new Payment Method (1 = Cash, 2 = E-Wallet)
            print("\n[bold yellow]Select New Payment Method:[/bold yellow]")
            print("[bold green][1][/bold green] Cash")
            print("[bold green][2][/bold green] E-Wallet")
            
            pay_choice = ask_input("Enter choice [1-2] (or 00 to go back)", r"^(1|2|00)$", "Please enter 1 for Cash, 2 for E-Wallet, or 00 to go back!")
            if pay_choice is None: return
            if pay_choice == "00":
                print("[yellow]↩️ Going back to choose Transaction ID...[/yellow]\n")
                continue # babalik sa pagpili ng Transaction ID
                
            payment_method = "Cash" if pay_choice == "1" else "E-Wallet"
            break
            
        # Ask for confirmation before saving
        if not ask_confirm(f"Change Transaction #{chosen_id} ({selected_tx['client_name']}) payment method from {selected_tx['payment_method']} to {payment_method}?"):
            clear_screen()
            print("[cyan]Update cancelled...[/cyan]\n")
            return
            
        # tatawagin ung PATCH API para isave ung bagong payment_method
        updated_tx = api_patch(f"/transactions/{chosen_id}", {"payment_method": payment_method})
        if updated_tx is None:
            return
            
        print(f"\n[bold green]✅ Transaction #{chosen_id} payment method updated to {payment_method}![/bold green]\n")
        showTable(updated_tx, "✅ Updated Transaction Record", TRANSACTION_COLUMNS)
        
        pauseDisplay()
        clear_screen()
        return


# Transactions Menu
def transactionsModule():
    clear_screen()
    while True:
        print(Panel.fit(
            "[bold aquamarine1]💵 TRANSACTIONS & PAYMENT RECORDS[/bold aquamarine1]\n"
            "[dim red]Cash & E-Wallet Payment Logs[/dim red]",
            border_style="cyan"
        ))

        print("[bold yellow]Select an Action:[/bold yellow]")
        print("[bold green][1][/bold green] [dark_red]View & Filter Transactions (Cash / E-Wallet / Totals)[/dark_red]")
        print("[bold green][2][/bold green] [dark_red]Update Payment Method (Cash / E-Wallet)[/dark_red]")
        print("[bold red][0][/bold red] Back to Main Menu\n")

        choice = Prompt.ask("[dim red]Enter option [0-2][/dim red]").strip()
        match choice:
            case "1":
                viewTransactionsMenu()
            case "2":
                clear_screen()
                print("[cyan]Updating transaction payment method...[/cyan]\n")
                updateTransactionPayment()
            case "0":
                print("[yellow]Returning to Main Menu...[/yellow]\n")
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 2.[/bold red]\n")


# Main Program
while True:
    userChoice = mainMenu()
    match userChoice:
        case "1":
            studioRental()
        case "2":
            luthieryModule()
        case "3":
            transactionsModule()
        case "0":
            print("[yellow]Exiting LA School of Rock System... Goodbye![/yellow]\n")
            break  
        case _:
            print("[bold red]Invalid option. Please choose between 0 and 3.[/bold red]\n")
