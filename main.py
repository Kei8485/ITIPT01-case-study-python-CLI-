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
    print("[bold green][3][/bold green] [dark_red]Music School (Lessons & Schedules)[/dark_red]")
    print("[bold green][4][/bold green] [dark_red]Transactions & Payment Records[/dark_red]")
    print("[bold magenta][5][/bold magenta] Daily Cash Flow Report [dim](<Owner Only>)[/dim]")
    print("[bold red][0][/bold red] Exit System\n")
    
    choice = Prompt.ask("[dim red]Enter option [0-5][/dim red]").strip()
    return choice

# View all studio bookings (GET /studio-rentals)
def viewStudioRentals():
    response = api_get("/studio-rentals") # uses the function from utils
    # stores the json list 
    
    if response is None: 
        return # if None that means server error
    
    if not response:
        print("[yellow]No studio bookings found in the system yet![/yellow]")
        pauseDisplay()
        clear_screen()
        return
    # shows the tables
    showTable(response, "🎸 All Studio Bookings", STUDIO_COLUMNS)
    pauseDisplay()
    clear_screen()
    
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
        print("[bold green][1][/bold green] [dark_red]View All Studio Bookings[/dark_red]")
        print("[bold green][2][/bold green] [dark_red]Add New Studio Booking[/dark_red]")
        print("[bold green][3][/bold green] [dark_red]Finish Booking & Confirm Payment[/dark_red]")
        print("[bold green][4][/bold green] [dark_red]Update Booking Details[/dark_red]")
        print("[bold green][5][/bold green] [dark_red]Delete / Cancel Booking[/dark_red]")
        print("[bold red][0][/bold red] Back to Main Menu\n")

        choice = Prompt.ask("[dim red]Enter option [0-5][/dim red]").strip()
        match choice:
            case "1":
                # show studio bookings
                clear_screen()
                print("[cyan]Loading all studio bookings...[/cyan]\n")
                viewStudioRentals() 
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
    
# - - - - - - - - - Transactions & Payment Records Module - - - - - - - - -

# View all transactions (GET /transactions)
def viewTransactions():
    transactions = api_get("/transactions") # kumukuha ng lahat ng transactions galing sa API
    
    if transactions is None:
        return # if None that means server error
        
    if not transactions: # pag walang laman ung transactions list
        print("[yellow]No transaction records found in the system yet![/yellow]")
        pauseDisplay()
        clear_screen()
        return
        
    # ipapakita ung table gamit ung TRANSACTION_COLUMNS blueprint
    showTable(transactions, "💵 All Transaction & Payment Records", TRANSACTION_COLUMNS)
    pauseDisplay()
    clear_screen()


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
        print("[bold green][1][/bold green] [dark_red]View All Transactions[/dark_red]")
        print("[bold green][2][/bold green] [dark_red]Update Payment Method (Cash / E-Wallet)[/dark_red]")
        print("[bold red][0][/bold red] Back to Main Menu\n")

        choice = Prompt.ask("[dim red]Enter option [0-2][/dim red]").strip()
        match choice:
            case "1":
                clear_screen()
                print("[cyan]Loading all transactions...[/cyan]\n")
                viewTransactions()
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
            print("[cyan]Adding new studio booking...[/cyan]\n")
        case "3":
            print("[cyan]Finishing booking & confirming payment...[/cyan]\n")
        case "4":
            transactionsModule()
        case "5":
            print("[cyan]Deleting studio booking...[/cyan]\n")
        case "0":
            print("[yellow]Returning to Main Menu...[/yellow]\n")
            break  
        case _:
            print("[bold red]Invalid option. Please choose between 0 and 5.[/bold red]\n")
