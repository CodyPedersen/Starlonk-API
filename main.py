from fastapi import FastAPI, Depends, Header, BackgroundTasks, status
from typing import Union
from sqlalchemy.orm import Session
from utils.database import engine, SessionLocal
from utils.data import refresh_satellite_data, log_data
from utils.schemas import SatelliteQuery
from utils.auth import authorize
import utils.predict as predict
import utils.models as models
import uuid
import os

# Create DB tables if DNE
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


@app.get("/satellites/")
async def get_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    param_dict = params.dict(exclude_none=True)

    query = db.query(models.Satellite) # Not query.all() as that returns a list

    # Filter list on each attribute in parameters
    for key, val in param_dict.items():
        query = query.filter(getattr(models.Satellite, key) == val)

    satellite_list = [s.to_dict() for s in query.all()]

    return {"satellites" : satellite_list}

   
@app.get("/predict/")
async def get_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    param_dict = params.dict(exclude_none=True)
    satellite_id = param_dict['satellite_id']
    epoch = param_dict['epoch']
    
    # Get satellite
    satellite = db.query(models.Satellite).filter(models.Satellite.satellite_id == satellite_id).first()

    satellite_prediction = predict.predict_location(satellite, epoch)

    return satellite_prediction


@app.get("/bulk_predict/")
async def get_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    param_dict = params.dict(exclude_none=True)
    epoch = param_dict['epoch']

    # Get all satellites in DB
    all_satellites = db.query(models.Satellite).all()

    # Get location prediction for all satellites
    satellite_predictions = []
    for satellite in all_satellites:
        satellite_prediction = predict.predict_location(satellite, epoch)
        satellite_predictions.append(satellite_prediction)

    return {"satellites" : satellite_predictions}

@app.post("/admin/refresh/", status_code=202)
@authorize
async def refresh_data(background_tasks : BackgroundTasks, db: Session = Depends(get_db), Authorization: Union[str, None] = Header(default=None)):
    pid = str(uuid.uuid4())
    background_tasks.add_task(refresh_satellite_data, db, pid)
    log_data("Refreshed satellite data")
    return {"status": "accepted", "pid" : pid}


@app.get("/admin/process/{process_id}")
@authorize
async def get_process(process_id, db: Session = Depends(get_db), Authorization: Union[str, None] = Header(default=None)):
    print(Authorization)
    process = db.query(models.Process).filter(models.Process.id == process_id).one()
    return {"process" : process.to_dict()}
    


# uvicorn main:app --reload


'''
    https://www.orekit.org/site-orekit-8.0/apidocs/org/orekit/files/ccsds/Keyword.html
    
    epoch: The epoch is the sequential calendar date when the satellite crossed the equator in an ascending (northerly) direction
    mean_motion: earth revolutions/day. 
        - Period (minutes) = (24*60)/mean_motion
    eccentricity: how far away from a perfect circle is the orbit around the earth
    inclination (degrees): measures the tilt of an object's orbit around earth's equator (https://en.wikipedia.org/wiki/Orbital_inclination)
    ra_of_asc_node (degrees): Right Ascension of the Ascending Node
    arg_of_pericenter (degrees): 
    mean_anomaly (degrees): 
    bstar: drag calculation

'''