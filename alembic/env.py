import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from alembic import context
from app.database import Base  # Import Base from your project
from app.models import *  # Import your models

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Bind metadata
target_metadata = Base.metadata

# Connection setup
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
