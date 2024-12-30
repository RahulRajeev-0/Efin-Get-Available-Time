# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from datetime import time, date
from typing import List, Dict


class UserCreate(BaseModel):
    name: str
    email: str
    time_zone: str  # User's timezone (e.g., "UTC", "Asia/Kolkata")


class UserResponse(UserCreate):
    id: int  # Return the user ID after creating the user

    class Config:
        orm_mode = True


class GeneralAvailabilityCreate(BaseModel):
    user_id: int
    day: str  # Day of the week (e.g., 'monday', 'tuesday', etc.)
    start_time: time
    end_time: time
    time_zone: str  # User's time zone (e.g., "UTC", "Asia/Kolkata")


class GeneralAvailabilityResponse(GeneralAvailabilityCreate):
    id: int  # ID of the general availability record

    class Config:
        orm_mode = True


class CustomAvailabilityBase(BaseModel):
    user_id: int
    date: date
    start_time: time
    end_time: time
    time_zone: str

class CustomAvailabilityCreate(CustomAvailabilityBase):
    pass

class CustomAvailabilityResponse(CustomAvailabilityBase):
    id: int

    class Config:
        orm_mode = True



class AvailabilityRequest(BaseModel):
    user_ids: List[int]
    startdate: str  # Date in dd-mm-yyyy format
    enddate: str    # Date in dd-mm-yyyy format
    timezone: str   # Time zone, e.g., 'Asia/Kolkata'

class CommonAvailabilityResponse(BaseModel):
    date: Dict[str, List[str]]  # Date as key and available time slots as list

    class Config:
        orm_mode = True