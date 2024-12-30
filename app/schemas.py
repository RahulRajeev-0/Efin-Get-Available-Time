# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
import time 
from typing import List


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
