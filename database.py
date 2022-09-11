import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
engine = create_engine(DATABASE_CONNECTION_URI) # Create connection to databse
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Individual sessions inherit from me
Base = declarative_base() # Used for models
