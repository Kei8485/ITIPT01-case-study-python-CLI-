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

LUTHIERY_QUESTIONS = [
    {"key": "client_name", "label": "Client Name", "pattern": r"^.+$", "err": "Cannot be empty!"},
    {"key": "contact_number", "label": "Contact Number (09XXXXXXXXX)", "pattern": r"^09\d{9}$", "err": "Must be 11 digits starting with 09!"},
    {"key": "instrument_type", "label": "Instrument Type (e.g. Electric Guitar, Bass)", "pattern": r"^.+$", "err": "Cannot be empty!"},
    {"key": "issue_description", "label": "Repair / Modification Issue", "pattern": r"^.+$", "err": "Cannot be empty!"},
    {"key": "estimated_cost", "label": "Estimated Service Cost (PHP)", "pattern": r"^[1-9]\d*(\.\d{1,2})?$", "err": "Must be a valid amount > 0!", "is_float": True}
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
    {"header": "Contact", "key": "contact_number"},
    {"header": "Instrument", "key": "instrument_type", "style": "yellow"},
    {"header": "Issue / Service", "key": "issue_description"},
    {"header": "Cost", "key": "estimated_cost", "style": "green", "justify": "right", "is_currency": True},
    {"header": "Status", "key": "status", "justify": "center", "is_status": True}
]

TRANSACTION_COLUMNS = [
    {"header": "TX ID", "key": "id", "style": "bold cyan", "justify": "center"},
    {"header": "Category", "key": "service_category", "style": "yellow"},
    {"header": "Ref ID", "key": "reference_id", "justify": "center"},
    {"header": "Client Name", "key": "client_name", "style": "bold white"},
    {"header": "Date", "key": "date", "style": "dim yellow"},
    {"header": "Payment Method", "key": "payment_method", "style": "bold magenta", "justify": "center"},
    {"header": "Amount Paid", "key": "amount_paid", "style": "green", "justify": "right", "is_currency": True},
    {"header": "Status", "key": "status", "justify": "center", "is_status": True}
]

# - - - - - - - - - Table Columns - - - - - - - - -


# - - - - - - - - - helper functions - - - - - - - - -
def showCannotConnectAPIServer():
    print("[bold red]Cannot connect to the API server! Ensure uvicorn is running.[/bold red]")
    
def pauseDisplay():
    Prompt.ask("[red] - - - Press Enter To Go Back - - - ").strip()
    clear_screen()

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
    
def ask_confirm(prompt_msg="Are you sure you want to proceed?"):
    """
    Asks the user for (y/n) confirmation.
    Loops until the user enters 'y' or 'n'.
    Returns True for 'y'/'yes', and False for 'n'/'no'.
    """
    while True:
        choice = Prompt.ask(f"\n[bold yellow]{prompt_msg} (y/n)[/bold yellow]").strip().lower()
        
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
            
        print("[bold red]❌ Invalid input! Please enter 'y' for Yes or 'n' for No.[/bold red]")
    
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
                if val in ("Paid", "Completed"):
                    color = "green"
                elif val == "In Progress":
                    color = "cyan"
                else:
                    color = "yellow"
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
        if f.get("is_int"):
            form_data[f["key"]] = int(val)
        elif f.get("is_float"):
            form_data[f["key"]] = float(val)
        else:
            form_data[f["key"]] = val
        
    return form_data

def step_by_step_edit(fields, current_data=None): # (kung anong question ilalagay)(kung anong data ilalagay) if alang data stays at None
    
    # Loops through fields with current values.
    # Supports: 000 (keep), 00 (go back), 0 (cancel).
    # Returns the updated dictionary, or None if cancelled.
    
    if current_data is None:
        current_data = {}
    
    is_editing = bool(current_data)  # True if editing, False if adding brand-new
    
    updated_info = {}
    for f in fields: # putting the info from the json file into the updated info
        updated_info[f["key"]] = current_data.get(f["key"], "")
    
    step = 0 # since naka list ung fields - naka base ung step ung key kung saang input na sya
    while step < len(fields): # condition if step is greater than the length stops the program
        current_field = fields[step] # kung anong question ang nakalagay
        # ex sa array 1 ay ung field ng client name question
        field_key = current_field["key"] # kinuhana ung key, papakita na ung mismoong question
        current_val = updated_info[field_key] # nilagay lng ung dating data na iuupdate ngayon
        
        action = "Editing" if is_editing else "Inputing"
        print(f"\n[dim cyan]{action} Field [{step + 1}/{len(fields)}]:[/dim cyan] [bold yellow]{current_field['label']}[/bold yellow]")
        # Only show current value & 000 shortcut if we are editing an existing item
        if is_editing and current_val != "":
            print(f"[pink]Current value: [bold green]{current_val}[/bold green]")
            shortcuts = "000=keep, 00=back, 0=cancel"
        else:
            shortcuts = "00=back, 0=cancel"
            
        user_val = Prompt.ask(f"[bold yellow]Enter value ({shortcuts})[/bold yellow]").strip()

        # [0] Cancel completely
        if user_val == "0":
            clear_screen()
            print("[cyan]Update cancelled...[/cyan]\n")
            return None

        # [00] Go back to the previous field
        if user_val == "00":
            if step > 0:
                step -= 1
                print("[yellow]↩️ Going back to previous field...[/yellow]")
            else:
                print("[bold red]⚠️ Already at the first field![/bold red]")
            continue

        # [000] Retain / Keep current value
        if is_editing and user_val == "000":
            print(f"[dim green]Keeping current value: {current_val}[/dim green]")
            step += 1
            continue

        # Regular input: Validate using Regex
        if re.match(current_field["pattern"], user_val):
            if current_field.get("is_int") or field_key == "hours":
                updated_info[field_key] = int(user_val)
            elif current_field.get("is_float"):
                updated_info[field_key] = float(user_val)
            else:
                updated_info[field_key] = user_val
            step += 1
        else:
            print(f"[bold red]❌ {current_field['err']}[/bold red]")
    return updated_info
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



def api_patch(endpoint, payload):
    try:
        response = requests.patch(f"{API_URL}{endpoint}", json=payload)
        
        if response.status_code == 200:
            # if it gets here, inside the api.py we already change the target id from booked to paid (andun ung logic sa api.py)
            return response.json() # if all valid returns the json
        
        error_msg = response.json().get("detail", f"HTTP {response.status_code}")        
        print(f"\n[bold red]❌ {error_msg}[/bold red]")
    except requests.exceptions.ConnectionError:
        print("[bold red]Cannot connect to the API.[/bold red]")
        showCannotConnectAPIServer()    
        
    pauseDisplay()
    return None # returns none of its there is a error

def api_put(endpoint, payload):
    try:
        response = requests.put(f"{API_URL}{endpoint}", json=payload)
        
        # 200 OK: Return the updated record
        if response.status_code == 200:
            return response.json()
            
        # If there's an error (e.g. 400 Already Paid, 404 ID Not Found, 422 Invalid Format)
        error_msg = response.json().get("detail", f"HTTP {response.status_code}")
        print(f"\n[bold red]❌ {error_msg}[/bold red]")
        
    except requests.exceptions.ConnectionError:
        print("[bold red]Cannot connect to the API.[/bold red]")
        showCannotConnectAPIServer()
    pauseDisplay()
    return None

def api_delete(endpoint):
    try:
        response = requests.delete(f"{API_URL}{endpoint}")
        
       
        if response.status_code == 200:
            return response.json()
            
        error_msg = response.json().get("detail", f"HTTP {response.status_code}")
        print(f"\n[bold red]❌ {error_msg}[/bold red]")
        
    except requests.exceptions.ConnectionError:
        print("[bold red]Cannot connect to the API.[/bold red]")
        showCannotConnectAPIServer()

    pauseDisplay()
    return None
    
# - - - - - - - - - API functions - - - - - - - - -
