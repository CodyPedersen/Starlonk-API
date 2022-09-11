from fastapi import FastAPI, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from data import refresh_satellite_data
from schemas import SatelliteQuery
import models
import data

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create a DB session for the call
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def get_home():
    return {"message" : "Starlink API. See <this site>/docs"}


# # Get all Starlink Satellites
# @app.get("/satellites/")
# async def get_satellites(db: Session = Depends(get_db)):
#     satellites = db.query(models.Satellite).all()
#     return {"satellites" : satellites}


@app.get("/satellites/")
async def get_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):

    param_dict = params.dict(exclude_none=True)

    query = db.query(models.Satellite) # Not query.all() as that returns a list

    # Filter list on each attribute in parameters
    for key, val in param_dict.items():
        query = query.filter(getattr(models.Satellite, key) == val)

    satellite_list = [s.to_dict() for s in query.all()]

    return {"satellites" : satellite_list}


@app.post("/refresh/")
async def refresh_data(db: Session = Depends(get_db)):
    refresh_satellite_data(db)
    return {"status": "success"}
   
   
# uvicorn main:app --reload