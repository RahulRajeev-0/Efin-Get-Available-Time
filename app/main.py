# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import crud, models, schemas
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# Create the tables in the database
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST endpoint to create a new user
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/general-availability/", response_model=schemas.GeneralAvailabilityResponse)
def create_general_availability(availability: schemas.GeneralAvailabilityCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_general_availability(db=db, availability=availability)
    except HTTPException as e:
        print("ERROR = ",e)
        raise HTTPException(status_code=400, detail="This availability already exists for the user or have overlaps with an existing availability")
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Database constraint violation error.")
    except Exception as e:
        # Log any unexpected errors and return a generic 500 error
        logging.error(f"Unexpected error: {str(e)}")



