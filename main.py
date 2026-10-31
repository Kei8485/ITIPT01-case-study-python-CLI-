import re
import requests
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from utils import clear_screen, ask_input, api_get, API_URL, api_post, pauseDisplay

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
    rentals = api_get("/studio-rentals") # uses the function from utils
    # stores the json list 
    
    if rentals is None: 
        return # if None that means server error
    
    if not rentals:
        print("[yellow]No studio bookings found in the system yet![/yellow]")
        pauseDisplay()
        clear_screen()
        return
    
    table = Table(title="🎸 All Studio Bookings", border_style="cyan")
    table.add_column("ID", style="bold cyan", justify="center")
    table.add_column("Client Name", style="bold white")
    table.add_column("Contact Number")
    table.add_column("Date Issued", style="dim yellow")
    table.add_column("Booking Date", style="yellow")
    table.add_column("Start Time", style="yellow")
    table.add_column("Hours", justify="center")
    table.add_column("Total Fee", style="green", justify="right")
    table.add_column("Status", justify="center")

    for r in rentals:
        color = "green" if r["status"] == "Paid" else "yellow"
        table.add_row( # row base on the column ^^^^^
            str(r["id"]),
            r["client_name"],
            r["contact_number"],
            r["date_issued"],
            r["date"],
            r["start_time"],
            str(r["hours"]),
            f"₱{r['total_fee']:,.2f}",
            f"[{color}]{r['status']}[/{color}]"
        )

    print(table)
    Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
    clear_screen()
    
# Add new Studio Booking
def addStudioBooking():
    
    while True:
        # To check if it can connect to the server
        api_get("/studio-rentals")
        
        print(Panel.fit(
            "[bold cyan]➕ ADD NEW STUDIO BOOKING[/bold cyan]\n"
            "[dim]Enter client & reservation details below[/dim]\n"
            "[dim yellow]Press [0] to cancel or go back[/dim yellow]",
            border_style="cyan"
        ))
        
        client_name = ask_input("Client / Band Name", r"^.+$", "Name cannot be empty!") # does the label component
        if not client_name: return
        contact_number = ask_input("Contact Number (09XXXXXXXXX)", r"^09\d{9}$", "Must be 11 digits starting with 09!")
        if not contact_number: return
        date = ask_input("Reservation Date (YYYY-MM-DD)",
        r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$",
        "Invalid date! Use YYYY-MM-DD with month 01-12 and day 01-31!")
        if not date: return
        start_time = ask_input("Start Time (e.g. 14:00)", r"^([01]\d|2[0-3]):[0-5]\d$", "Use 24-hour HH:MM format (e.g. 14:00)!")
        if not start_time: return
        hours_input = ask_input("Number of Hours", r"^[1-9]\d*$", "Hours must be a whole number greater than 0!")
        if not hours_input: return
        
        
        # gets stored here
        new_booking = {
            "client_name": client_name,
            "contact_number": contact_number,
            "date": date,
            "start_time": start_time,
            "hours": hours_input
        }
        
        response = api_post("/studio-rentals",new_booking)
        
        if response is None:
            return    
            
        # if its successful it will proceed here and it will return the r as the json file
        # we show that the data that was sent was a success
        table = Table(title="✅ New Studio Booking Added", border_style="green")
        table.add_column("ID", style="bold cyan", justify="center")
        table.add_column("Client Name", style="bold white")
        table.add_column("Contact Number")
        table.add_column("Date Issued", style="dim yellow")
        table.add_column("Booking Date", style="yellow")
        table.add_column("Start Time", style="yellow")
        table.add_column("Hours", justify="center")
        table.add_column("Total Fee", style="green", justify="right")
        table.add_column("Status", justify="center")
        
        table.add_row(
            str(response["id"]), # turns into a string because its a int
            response["client_name"], 
            response["contact_number"],
            response["date_issued"],
            response["date"],
            response["start_time"],
            str(response["hours"]),
            f"₱{response['total_fee']:,.2f}",
            f"[yellow]{response['status']}[/yellow]"
        )
        
        print(table)
        Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
        clear_screen()
        return

#Update Status for finished studio booking
def finishStudioBooking():
    while True:
        # --- REQUEST 1: GET all bookings & filter only "Booked" ---
        try:
            response = requests.get(f"{API_URL}/studio-rentals")
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        
        if response.status_code != 200:
            print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        
        rentals = response.json() # REMEMBER SINCE GET METHOD TO KINUKUHA NYA UNG JSON NA DATA
        booked_rentals = [r for r in rentals if r["status"] == "Booked"] # may r sa unahan para makuha ung lahat ng data
        
        if not booked_rentals:
            print("[yellow]No unpaid 'Booked' studio reservations found![/yellow]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            clear_screen()
            return
        # if merong laman ung book rentals
        table = Table(title="🎸 Unpaid Studio Bookings (Status: Booked)", border_style="cyan")
        table.add_column("ID", style="bold cyan", justify="center")
        table.add_column("Client Name", style="bold white")
        table.add_column("Contact")
        table.add_column("Date Issued", style="dim yellow")
        table.add_column("Booking Date", style="yellow")
        table.add_column("Start Time", style="yellow")
        table.add_column("Hours", justify="center")
        table.add_column("Total Fee", style="green", justify="right")
        table.add_column("Status", justify="center")
        for r in booked_rentals:
            table.add_row(
                str(r["id"]),
                r["client_name"],
                r["contact_number"],
                r.get("date_issued", "N/A"),
                r["date"],
                r["start_time"],
                str(r["hours"]),
                f"₱{r['total_fee']:,.2f}",
                f"[yellow]{r['status']}[/yellow]"
            )
        print(table)
        print("[red](<Type 0 at any time to cancel and go back>)\n")
        
        
        # Ask which Booking ID to finish (must be in booked_rentals!)
        valid_ids = [str(r["id"]) for r in booked_rentals]
        while True:
            rental_id = ask_input("Enter Booking ID to Confirm Payment", r"^[1-9]\d*$", "ID must be a valid number!")
            if not rental_id: return
            if rental_id in valid_ids:
                break
            print(f"[bold red]❌ Booking ID #{rental_id} is not in the unpaid list above! Choose from: {', '.join(valid_ids)}[/bold red]")
        
        # Ask for Payment Method (1 = Cash, 2 = E-Wallet)
        print("\n[bold yellow]Select Payment Method:[/bold yellow]")
        print("[bold green][1][/bold green] Cash")
        print("[bold green][2][/bold green] E-Wallet")
        pay_choice = ask_input("Enter choice [1-2]", r"^[12]$", "Please enter 1 for Cash or 2 for E-Wallet!")
        if not pay_choice: return
        payment_method = "Cash" if pay_choice == "1" else "E-Wallet"
        
        try:
            patch_res = requests.patch(
                f"{API_URL}/studio-rentals/{rental_id}/pay",
                json={"payment_method": payment_method}
            )
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            return    
        
        if patch_res.status_code == 404:
            print(f"\n[bold red]❌ Booking ID #{rental_id} not found![/bold red]")
        elif patch_res.status_code == 400:
            print(f"\n[bold red]❌ Booking ID #{rental_id} is already Paid![/bold red]")
        elif patch_res.status_code == 200:
            updated = patch_res.json()
            print(f"\n[bold green]✅ Payment Confirmed! Booking #{updated['id']} ({updated['client_name']}) is now PAID via {payment_method}![/bold green]")
            print("[dim green]Transaction record has been automatically created and saved to data.json.\n[/dim green]")
            paid_table = Table(title="✅ Updated Studio Booking", border_style="green")
            paid_table.add_column("ID", style="bold cyan", justify="center")
            paid_table.add_column("Client Name", style="bold white")
            paid_table.add_column("Contact")
            paid_table.add_column("Date Issued", style="dim yellow")
            paid_table.add_column("Booking Date", style="yellow")
            paid_table.add_column("Start Time", style="yellow")
            paid_table.add_column("Hours", justify="center")
            paid_table.add_column("Total Fee", style="green", justify="right")
            paid_table.add_column("Status", justify="center")
            paid_table.add_row(
                str(updated["id"]),
                updated["client_name"],
                updated["contact_number"],
                updated.get("date_issued", "N/A"),
                updated["date"],
                updated["start_time"],
                str(updated["hours"]),
                f"₱{updated['total_fee']:,.2f}",
                f"[bold green]{updated['status']}[/bold green]"
            )
            print(paid_table)
        else:
            print(f"\n[bold red]Error: HTTP {patch_res.status_code}[/bold red]")
        Prompt.ask("\n[red] - - - Press Enter To Go Back - - - ").strip()
        clear_screen()
        
# Updating all details for Put API
def udpateStudioBooking():
    while True:
        clear_screen()
        # vvvvvvv SHOWING OF TABLES PALANG vvvvvvv #

        # GET muna dito
        try:
            response = requests.get(f"{API_URL}/studio-rentals")
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        if response.status_code != 200:
            print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        
        # if all correct get the response
        rentals = response.json()
        
        #showing booked rentals only and not yet paid
        booked_rentals = [r for r in rentals if r ["status"] == "Booked"] # lalagay na dito ung data
        # MAIN JOB ^^^^^^ for showing the filtered data
        
        # if empty
        if not booked_rentals:
            print("[yellow]No editable 'Booked' studio reservations found![/yellow]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            clear_screen()
            return
        
        ##display if all is valid
        # Display table of editable bookings
        table = Table(title="📝 Editable Studio Bookings (Status: Booked)", border_style="cyan")
        table.add_column("ID", style="bold cyan", justify="center")
        table.add_column("Client Name", style="bold white")
        table.add_column("Contact")
        table.add_column("Booking Date", style="yellow")
        table.add_column("Start Time", style="yellow")
        table.add_column("Hours", justify="center")
        table.add_column("Total Fee", style="green", justify="right")
        for r in booked_rentals:
            table.add_row(
                str(r["id"]),
                r["client_name"],
                r["contact_number"],
                r["date"],
                r["start_time"],
                str(r["hours"]),
                f"₱{r['total_fee']:,.2f}"
            )
        print(table)
        print("[red](<Type 0 at any time to cancel and go back>)\n")        
        # for displaying the input fields
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
        print(Panel.fit(
            f"[bold cyan]✏️ EDITING BOOKING #{rental_id}[/bold cyan]\n"
            "[dim]Review current values below. Shortcuts:[/dim]\n"
            "[bold green][000][/bold green] Retain / Keep current value\n"
            "[bold yellow][00][/bold yellow]  Go back to previous field\n"
            "[bold red][0][/bold red]   Cancel and return to menu",
            border_style="cyan"
        ))
        
        # Ask the information that will be updated
                # Print the current details table
        curr_table = Table(title=f"📋 Current Details for Booking #{rental_id}", border_style="yellow")
        curr_table.add_column("Field", style="bold white")
        curr_table.add_column("Current Value", style="bold green")

        curr_table.add_row("Client / Band Name", selected_booking["client_name"])
        curr_table.add_row("Contact Number", selected_booking["contact_number"])
        curr_table.add_row("Reservation Date", selected_booking["date"])
        curr_table.add_row("Start Time", selected_booking["start_time"])
        curr_table.add_row("Number of Hours", str(selected_booking["hours"]))
        print(curr_table)

        # 2. Define the fields in order with their validation patterns
        fields = [
            {"key": "client_name", "label": "Client / Band Name", "pattern": r"^.+$", "err": "Name cannot be empty!"},
            {"key": "contact_number", "label": "Contact Number (09XXXXXXXXX)", "pattern": r"^09\d{9}$", "err": "Must be 11 digits starting with 09!"},
            {"key": "date", "label": "Reservation Date (YYYY-MM-DD)", "pattern": r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", "err": "Invalid date! Use YYYY-MM-DD!"},
            {"key": "start_time", "label": "Start Time (HH:MM)", "pattern": r"^([01]\d|2[0-3]):[0-5]\d$", "err": "Use 24-hour HH:MM format (e.g. 14:00)!"},
            {"key": "hours", "label": "Number of Hours", "pattern": r"^[1-9]\d*$", "err": "Hours must be a whole number greater than 0!"}
        ]

        # 3. Start with the existing values as default
        updated_information = {
            "client_name": selected_booking["client_name"],
            "contact_number": selected_booking["contact_number"],
            "date": selected_booking["date"],
            "start_time": selected_booking["start_time"],
            "hours": selected_booking["hours"]
        }

        # 4. Step-by-step navigation loop
        step = 0 # since naka list ung fields - naka base ung step ung key kung saang input na sya
        while step < len(fields): # condition if step is greater than the length stops the program
            current_field = fields[step] # current field na nakalagay kung pang ilan sa (array)
            field_key = current_field["key"] # since na access na ung id ng array kukunin nya kung anong key un (if client name or contact number etc)
            current_val = updated_information[field_key] # kung anong information ung inuupdate mo

            print(f"\n[dim cyan]Editing Field [{step + 1}/{len(fields)}]:[/dim cyan] [bold yellow]{current_field['label']}[/bold yellow]")
            print(f"[dim]Current value:[/dim] [bold green]{current_val}[/bold green]")
            user_val = Prompt.ask(f"[bold yellow]Enter new value (000=keep, 00=back, 0=cancel)[/bold yellow]").strip()

            # [0] Cancel completely
            if user_val == "0":
                clear_screen()
                print("[cyan]Update cancelled...[/cyan]\n")
                return

            # [00] Go back to the previous field
            if user_val == "00":
                if step > 0:
                    step -= 1
                    print("[yellow]↩️ Going back to previous field...[/yellow]")
                else:
                    print("[bold red]⚠️ Already at the first field![/bold red]")
                continue

            # [000] Retain / Keep current value
            if user_val == "000":
                print(f"[dim green]Keeping current value: {current_val}[/dim green]")
                step += 1
                continue

            # Regular input: Validate using Regex
            if re.match(current_field["pattern"], user_val):
                if field_key == "hours":
                    updated_information[field_key] = int(user_val)
                else:
                    updated_information[field_key] = user_val
                step += 1
            else:
                print(f"[bold red]❌ {current_field['err']}[/bold red]")
        
        # doing the PUT API Request
        try: 
            put_res = requests.put(f"{API_URL}/studio-rentals/{rental_id}", json=updated_information)
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            return
        if put_res.status_code == 200:
            ##creates a table showing that its been added
            updated = put_res.json() # since the json=updated_information is not completed
                                     # when we put updated_information, it inside the data now so this completes the json with the non inputed datas
            print(f"\n[bold green]✅ Booking #{rental_id} successfully updated![/bold green]\n")
            success_table = Table(title="✅ Updated Booking Details", border_style="green")
            success_table.add_column("ID", style="bold cyan", justify="center")
            success_table.add_column("Client Name", style="bold white")
            success_table.add_column("Contact")
            success_table.add_column("Booking Date", style="yellow")
            success_table.add_column("Start Time", style="yellow")
            success_table.add_column("Hours", justify="center")
            success_table.add_column("Total Fee", style="green", justify="right")
            success_table.add_row(
                str(updated["id"]),
                updated["client_name"],
                updated["contact_number"],
                updated["date"],
                updated["start_time"],
                str(updated["hours"]),
                f"₱{updated['total_fee']:,.2f}"
            )
            print(success_table)
    
        else:
            print(f"\n[bold red]Error: HTTP {put_res.status_code} - {put_res.text}[/bold red]")
            
        Prompt.ask("\n[red] - - - Press Enter To Continue - - - ").strip()
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
            case "0":
                print("[yellow]Returning to Main Menu...[/yellow]\n")
                break
            case _:
                clear_screen()
                print("[bold red]Invalid option. Please choose between 0 and 5.[/bold red]\n")
    
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
            print("[cyan]Updating booking details...[/cyan]\n")
        case "5":
            print("[cyan]Deleting studio booking...[/cyan]\n")
        case "0":
            print("[yellow]Returning to Main Menu...[/yellow]\n")
            break  
        case _:
            print("[bold red]Invalid option. Please choose between 0 and 5.[/bold red]\n")
