"""
Database connection.

Default: SQLite (file pharmacy.db) -> koi server install nahi karna parta.
PostgreSQL/MySQL chahiye to .env file mein DATABASE_URL set karein, jaise:
    DATABASE_URL=postgresql://user:password@localhost:5432/pharmacy_db
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db")

# SQLite ko FastAPI ke multiple threads ke liye yeh option chahiye
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
