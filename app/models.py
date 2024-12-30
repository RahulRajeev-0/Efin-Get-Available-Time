from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from app.database import Base


# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    time_zone = Column(String, nullable=False)  # User's default timezone
    
    # Relationships
    general_availability = relationship("GeneralAvailability", back_populates="user")
    custom_availability = relationship("CustomAvailability", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")


# General Availability Table (Weekly Availability)
class GeneralAvailability(Base):
    __tablename__ = "general_availability"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day = Column(String, nullable=False)  # Day of the week (e.g., "Monday", "Tuesday")
    start_time = Column(Time, nullable=False)  # Start time for the availability
    end_time = Column(Time, nullable=False)    # End time for the availability
    time_zone = Column(String, nullable=False)  # Specific timezone for the availability

    # Relationship
    user = relationship("User", back_populates="general_availability")

    # Ensure uniqueness per user, day, start time, and end time
    __table_args__ = (
        UniqueConstraint("user_id", "day", "start_time", "end_time", name="unique_general_availability"),
    )


# Custom Availability Table (Specific Dates)
class CustomAvailability(Base):
    __tablename__ = "custom_availability"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)  # Specific date
    start_time = Column(Time, nullable=False)  # Start time
    end_time = Column(Time, nullable=False)    # End time
    time_zone = Column(String, nullable=False)  # Specific timezone

    # Relationship
    user = relationship("User", back_populates="custom_availability")

    # Ensure uniqueness per user, date, start time, and end time
    __table_args__ = (
        UniqueConstraint("user_id", "date", "start_time", "end_time", name="unique_custom_availability"),
    )


# Schedule Table (Tracks Scheduled Events)
class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)  # Date of the event
    start_time = Column(Time, nullable=False)  # Event start time
    end_time = Column(Time, nullable=False)    # Event end time
    description = Column(String, nullable=True)  # Description of the event

    # Relationship
    user = relationship("User", back_populates="schedules")

    # Prevent overlapping or duplicate schedules for the same user
    __table_args__ = (
        UniqueConstraint("user_id", "date", "start_time", "end_time", name="unique_schedule"),
    )
