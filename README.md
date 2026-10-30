# 🎸 All-in-One Music Production Facility — Management API

> A local backend system built with FastAPI to monitor daily operations, streamline record-keeping across all services, and automatically generate daily cash flow reports.

---

## 🏢 1. Business Overview & Profile

- **Location:** Cabanatuan City, Nueva Ecija
- **Key Personnel:** Owner, 1 Sound Engineer, 2 Music Teachers
- **Target Customers:** Music professionals, hobbyists, and enthusiasts
- **Products & Services:**

1. **Studio Rentals:** Hourly band rehearsal and recording studio.
2. **Luthiery Services:** String instrument repair and modification.
3. **Music School:** Instrument instruction (guitar, bass, drums).

## ⚠️ 2. Existing Process & Problems

- **Current Workflow:** Physical record books + Facebook Messenger chats. Cash and e-wallet payments stored in a cash box.
- **The Problem:** Highly vulnerable to human error. Slow retrieval of customer history and schedules. No centralized way to track daily operations and financial inflows.

## 💡 3. System Architecture

- **Language:** Python
- **API Framework:** FastAPI (clean routing, Pydantic validation, automatic Swagger UI)
- **Data Storage:** Local JSON file (`data.json`) for self-contained persistence
- **Server Environment:** ASGI server (`uvicorn`)
- **Testing:** Postman & Swagger UI (`[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`)

---

## ⚙️ 4. API Features & Modules

### Role-Based Access Control (`X-Role` Header)

- **`staff`:** Can perform CRUD operations on schedules and log transactions. Restricted from owner endpoints (`403 Forbidden`).
- **`owner`:** Full administrative privileges, can view reports, modify prices, and manage settings.

### Core Modules (CRUD)

- **🎸 Studio Rentals:** Manage reservations and equipment allocations.
- **🔧 Luthiery Services:** Manage repair jobs and statuses (`Pending`, `In Progress`, `Completed`).
- **🎵 Music School:** Manage student schedules and instructor assignments.
- **💵 Transactions:** Manage cash and e-wallet payment logs.

### Generated Reports

- **📊 Daily Cash Flow Report:** Owner-only endpoint aggregating revenue and receivables.
- **📄 Live JSON Data:** Real-time persistence to `data.json`.

### HTTP Status Codes

- `200 OK` — Successful retrieval or update
- `201 Created` — Successful resource creation
- `204 No Content` — Successful resource deletion
- `403 Forbidden` — Unauthorized role access
- `404 Not Found` — Resource ID does not exist

---

## 🚀 5. Getting Started (Development Setup)

Follow these steps to set up the project locally:

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate

```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn

```

### 3. Configure VS Code Interpreter

1. Press `Ctrl + Shift + P` in VS Code.
2. Type `Python: Select Interpreter` and press Enter.
3. Select `.\venv\Scripts\python.exe` (or the one labeled `'venv': venv`).

### 4. Create Initial API File (`main.py`)

```python
from fastapi import FastAPI

app = FastAPI(title="Music Facility Management API")

@app.get("/")
def root():
    return {"message": "Music Facility API is running!"}

uvicorn api:app --reload
to open the api server

```

### 5. Optional Styling Tools

To select terminal colors (if using rich):

```bash
python -m rich.color

```

### 6. Do the UI For the mainMenu

### 7. Do the Models

```bash
from pydantic import BaseModel
```

needs this for fast API

### 7. Create a function that gets the API

```bash
import requests

```
