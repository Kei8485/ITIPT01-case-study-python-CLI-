from pydantic import BaseModel, Field

#things that will be inputed for the user
class StudioRentalInput(BaseModel):
    client_name: str = Field(min_length=1)                        # Cannot be empty
    contact_number: str = Field(pattern=r"^09\d{9}$")             # PH number: 09 + 9 digits
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")             # YYYY-MM-DD
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$") # HH:MM (00:00 to 23:59)
    hours: int = Field(gt=0)                                      # Greater than 0

# model para sa Luthiery Services (Guitar Repairs & Mods)
class LuthieryInput(BaseModel):
    client_name: str = Field(min_length=1)                        # Cannot be empty
    contact_number: str = Field(pattern=r"^09\d{9}$")             # PH number: 09 + 9 digits
    instrument_type: str = Field(min_length=1)                    # e.g. Electric Guitar, Bass
    issue_description: str = Field(min_length=1)                  # Repair / Mod details
    estimated_cost: float = Field(gt=0)                           # Service fee > 0

# model para sa pag-update ng status ng repair (Pending -> In Progress)
class LuthieryStatusInput(BaseModel):
    status: str                                                   # "Pending" or "In Progress"

class ConfirmPaymentInput(BaseModel):
    payment_method: str   # "Cash" or "E-Wallet"
