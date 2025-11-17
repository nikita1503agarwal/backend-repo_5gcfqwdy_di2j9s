import os
from datetime import datetime, date
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Booking

app = FastAPI(title="MFK Autocare ECU Remapping API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookingResponse(BaseModel):
    id: str
    message: str


@app.get("/")
def read_root():
    return {"message": "MFK Autocare API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Business rules
WORKING_DAYS = {0, 1, 2, 3, 4}  # Mon-Fri
TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00"
]


def is_working_day(d: date) -> bool:
    return d.weekday() in WORKING_DAYS


@app.get("/api/availability/{day}")
def get_availability(day: str):
    """Return available time slots for a given date (YYYY-MM-DD) excluding already booked slots."""
    try:
        d = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if not is_working_day(d):
        return {"date": day, "available": []}

    existing = get_documents("booking", {"date": day})
    booked = {doc.get("time") for doc in existing}
    available = [t for t in TIME_SLOTS if t not in booked]
    return {"date": day, "available": available}


@app.post("/api/book", response_model=BookingResponse)
def create_booking(booking: Booking):
    # Validate working day
    try:
        d = date.fromisoformat(booking.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if not is_working_day(d):
        raise HTTPException(status_code=400, detail="Selected date is not a working day (Mon-Fri)")

    # Prevent double-booking same slot
    existing = get_documents("booking", {"date": booking.date, "time": booking.time})
    if existing:
        raise HTTPException(status_code=409, detail="This time slot is already booked")

    inserted_id = create_document("booking", booking)
    return BookingResponse(id=inserted_id, message="Booking confirmed")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
