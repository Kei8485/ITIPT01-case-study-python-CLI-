import os
import re
import requests
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


API_URL = "http://127.0.0.1:8000"


# - - - - - - - - - Questions - - - - - - - - -

STUDIO_QUESTIONS = [
    {"key": "client_name", "label": "Client / Band Name", "pattern": r"^.+$", "err": "Cannot be empty!"},
    {"key": "contact_number", "label": "Contact Number (09XXXXXXXXX)", "pattern": r"^09\d{9}$", "err": "Must be 11 digits starting with 09!"},
    {"key": "date", "label": "Reservation Date (YYYY-MM-DD)", "pattern": r"^\d{4}-\d{2}-\d{2}$", "err": "Use YYYY-MM-DD!"},
    {"key": "start_time", "label": "Start Time (HH:MM)", "pattern": r"^([01]\d|2[0-3]):[0-5]\d$", "err": "Use HH:MM format!"},
    {"key": "hours", "label": "Number of Hours", "pattern": r"^[1-9]\d*$", "err": "Must be > 0!", "is_int": True}
]

# - - - - - - - - - Questions - - - - - - - - -



# - - - - - - - - - Table Columns - - - - - - - - -
STUDIO_COLUMNS = [
    {"header": "ID", "key": "id", "style": "bold cyan", "justify": "center"},
    {"header": "Client Name", "key": "client_name", "style": "bold white"},
    {"header": "Contact", "key": "contact_number"},
    {"header": "Booking Date", "key": "date", "style": "yellow"},
    {"header": "Start Time", "key": "start_time", "style": "yellow"},
    {"header": "Hours", "key": "hours", "justify": "center"},
    {"header": "Total Fee", "key": "total_fee", "style": "green", "justify": "right", "is_currency": True},
    {"header": "Status", "key": "status", "justify": "center", "is_status": True} 
]

LUTHIERY_COLUMNS = [
    {"header": "ID", "key": "id", "style": "bold cyan", "justify": "center"},
    {"header": "Client Name", "key": "client_name", "style": "bold white"},
    {"header": "Instrument", "key": "instrument_type", "style": "yellow"},
    {"header": "Issue", "key": "issue_description"},
    {"header": "Cost", "key": "estimated_cost", "style": "green", "is_currency": True},
    {"header": "Status", "key": "status", "justify": "center", "is_status": True}
]

# - - - - - - - - - Table Columns - - - - - - - - -


# - - - - - - - - - helper functions - - - - - - - - -
def showCannotConnectAPIServer():
    print("[bold red]Cannot connect to the API server! Ensure uvicorn is running.[/bold red]")
    
def pauseDisplay():
    Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()

def clear_screen():
    os.system('cls')
    
def invalidInputDisplay():
    print("[bold red]❌ Invalid Input! Please check the following fields:[/bold red]")
    
def showTypeZero():
    print("[dim]Please try again (or type 0 to cancel).\n[/dim]")
    
def showHTTPError(response):
    print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
    
# showing heading panel
def showHeadingPanel(title, description):
    print(Panel.fit(
        f"[bold cyan]{title}[/bold cyan]\n"
        f"[dim]{description}[/dim]\n"
        "[dim yellow]Press [0] to cancel or go back[/dim yellow]",
        border_style="cyan"
    ))
    
#displaying table
def showTable(data, title, columns):
    #data us the response from the api
    #creates the table column
    table = Table(title=title, border_style="cyan")
    # loops the dictionary I set above 
    for col in columns:
        table.add_column(
            col["header"], # at the top of the table 
            style=col.get("style", "white"), 
            justify=col.get("justify", "left")
        )
    
    
    # if its just 1 data it covers it up with a list so it can still run
    if isinstance(data, dict):
        data = [data] 
        
    #outer loop
    for d in data:
        row = []
        # Loop through each column and grab the matching value from d
        # inner loop
        for col in columns:
            key_name = col["key"]  # looks at the blueprint 
            val = d.get(key_name, "N/A") # opens the data and gets the data with that key name
            # example im in the key of client name then when I use the get 
            # it gets the client name of that key 

            # check if the key is_currency true
            # if its true that means we can put a peso sign when displaying the table
            if col.get("is_currency") and isinstance(val, (int, float)): # check if that variable is int or float
                val = f"₱{val:,.2f}"

            # check if the key is is_status true
            # if it is, we put the label of the status with color
            elif col.get("is_status"):
                color = "green" if val in ("Paid", "Completed") else "yellow"
                val = f"[{color}]{val}[/{color}]"
            else:
                # turning it into a string to be dispayed
                val = str(val)

            row.append(val)

        # Unpack the list into table.add_row using the asterisk (*)
        table.add_row(*row)
    print(table)    

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
        
def collect_form_inputs(question): # collects the json data format of the question
    # Loops through a list of fields and gathers inputs using ask_input.
    # If the user types 0 at any time, it immediately cancels and returns None.
    
    form_data = {}
    for f in question:
        val = ask_input(f["label"], f["pattern"], f["err"]) # using the input function
        if val is None:
            return  # User typed 0 to cancel
        
        # Convert numbers if needed
        form_data[f["key"]] = int(val) if f.get("is_int") else val
        
    return form_data
# - - - - - - - - - helper functions - - - - - - - - -



# - - - - - - - - - API functions - - - - - - - - -
def api_get(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}") # gets the response so that we know its for rental
        if response.status_code == 200:
            return response.json()
        print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
    except requests.exceptions.ConnectionError:
        showCannotConnectAPIServer()

    pauseDisplay()
    return None

def api_post(endpoint, payload): # endpoint is the path
                                 # payload is the data
    try: # the new_booking gets sent in the API
        response = requests.post(f"{API_URL}{endpoint}", json=payload)
    except requests.exceptions.ConnectionError:
        showCannotConnectAPIServer()
        pauseDisplay()
        return None
    
    if response.status_code == 422: #
            clear_screen()
            invalidInputDisplay()
            for err in response.json()["detail"]:
                field_name = err["loc"][-1]
                print(f"   [yellow]• {field_name}[/yellow] has an invalid format or value.")
            showTypeZero()
            return None
    
    if response.status_code != 201:
        showHTTPError(response)
        pauseDisplay()
        return None
    
    return response.json()
# - - - - - - - - - API functions - - - - - - - - -
