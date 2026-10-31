import os
import re
import requests
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


API_URL = "http://127.0.0.1:8000"

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
