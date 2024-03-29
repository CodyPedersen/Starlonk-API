"""Database/Session initialization functionality"""
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


#  Generate db session (for use with FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv()

# Database Setup
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')

DATABASE_CONNECTION_URI = f'postgresql://{user}:{password}@{host}:{port}/{database}'
print(DATABASE_CONNECTION_URI)

# SQL Alchemy
engine = create_engine(DATABASE_CONNECTION_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
