import os
import requests
import re 
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

API_URL = "http://127.0.0.1:8000"

def clear_screen():
    os.system('cls')
    

def ask_input(label, pattern, error_msg): # component for labels
    while True:
        print()
        value = Prompt.ask(f"[bold yellow]{label}[/bold yellow]").strip()
        if value == "0":
            clear_screen()
            print("[cyan]Cancelled...[/cyan]\n")
            return None # returns 2 times so it returns to the main menu
        if re.match(pattern, value):
            return value
        print(f"[bold red]❌ {error_msg}[/bold red]")

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

    rentals = response.json() # gets the response so that we know its for rental

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
        try:
            response = requests.get(f"{API_URL}/studio-rentals")
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        
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
        
        try: # the new_booking gets sent in the API
            response = requests.post(f"{API_URL}/studio-rentals", json=new_booking)
        except requests.exceptions.ConnectionError:
            print("[bold red]Cannot connect to the API.[/bold red]")
            Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
            return
        
        if response.status_code == 422:
                clear_screen()
                print("[bold red]❌ Invalid Input! Please check the following fields:[/bold red]")
                for err in response.json()["detail"]:
                    field_name = err["loc"][-1]
                    print(f"   [yellow]• {field_name}[/yellow] has an invalid format or value.")
                print("[dim]Please try again (or type 0 to cancel).\n[/dim]")
                continue   # <-- Loops back to the top so the user can retry!
        
        if response.status_code != 201:
            print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
            return
        
        # if its successful it will proceed here and it will return the r as the json file
        r = response.json()
        
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
            str(r["id"]), # turns into a string because its a int
            r["client_name"], 
            r["contact_number"],
            r["date_issued"],
            r["date"],
            r["start_time"],
            str(r["hours"]),
            f"₱{r['total_fee']:,.2f}",
            f"[yellow]{r['status']}[/yellow]"
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
        print("[dim](<Type 0 at any time to cancel and go back>)[/dim]\n")
        
        
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
