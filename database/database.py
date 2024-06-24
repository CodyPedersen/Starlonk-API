"""Database/Session initialization functionality"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from config import Config as cfg


# Generate db session (for use with FastAPI)
def get_db():
    """Yield and close a db"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv()

# Database Setup
HOST = cfg.DB_HOST
USER = cfg.DB_USER
PASSWORD = cfg.DB_PASSWORD
PORT = cfg.DB_PORT
DATABASE = cfg.DB_NAME

DATABASE_CONNECTION_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

# SQL Alchemy
engine = create_engine(DATABASE_CONNECTION_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
