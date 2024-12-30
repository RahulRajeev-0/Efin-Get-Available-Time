from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: "postgresql://user:password@localhost/dbname"

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# SessionLocal: Used to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Used for model class inheritance
Base = declarative_base()
