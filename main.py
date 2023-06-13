"""Main - houses REST API endpoint routers"""
import uuid
from typing import Union
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from ariadne import graphql_sync
from gql import schema
from fastapi import FastAPI, Request, Depends, Header, BackgroundTasks

from utils.database import engine, get_db
from utils.data import refresh_satellite_data, log_data
from api.schemas import SatelliteQuery
from api.auth import authorize
import utils.predict as predict
import utils.models as models

# Create DB tables if DNE
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def get_home():
    """Currently inactive"""
    return {"message": "Starlink API. See /docs"}


@app.get("/satellites/")
async def get_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    """Return all satellites, filtered on any satellite attribute"""

    param_dict = params.dict(exclude_none=True)

    # Not query.all() as that returns a list
    query = db.query(models.Satellite)

    # Filter list on each attribute in parameters
    for key, val in param_dict.items():
        query = query.filter(getattr(models.Satellite, key) == val)

    satellite_list = [s.to_dict() for s in query.all()]

    return {"satellites": satellite_list}


@app.get("/predict/")
async def predict_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    """Predict the location of a single satellite for a given epoch"""

    param_dict = params.dict(exclude_none=True)
    satellite_id = param_dict['satellite_id']
    epoch = param_dict['epoch']

    # Get satellite
    satellite = db.query(models.Satellite).filter(
        models.Satellite.satellite_id == satellite_id).first()

    satellite_prediction = predict.predict_location(satellite, epoch)

    return satellite_prediction


@app.get("/bulk_predict/")
async def get_bulk_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    """Predict all satellite location for a given epoch"""

    param_dict = params.dict(exclude_none=True)
    epoch = param_dict['epoch']

    # Get all satellites in DB
    all_satellites = db.query(models.Satellite).all()

    # Get location prediction for all satellites
    satellite_predictions = []
    for satellite in all_satellites:
        satellite_prediction = predict.predict_location(satellite, epoch)
        satellite_predictions.append(satellite_prediction)

    return {"satellites": satellite_predictions}


@app.post("/admin/refresh/", status_code=202)
@authorize
async def refresh_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    Authorization: Union[str, None] = Header(default=None)
):
    """Pull data from NORAD data sets and update DB with data"""

    pid = str(uuid.uuid4())
    background_tasks.add_task(refresh_satellite_data, db, pid)
    log_data("Refreshed satellite data")

    return {
        "status": "accepted",
        "pid": pid
    }


@app.get("/admin/process/{process_id}")
@authorize
async def get_process(
    process_id,
    db: Session = Depends(get_db),
    Authorization: Union[str, None] = Header(default=None)
    ):
    """Get the status given process (refresh)"""

    process = db.query(models.Process).filter(
        models.Process.id == process_id).one()
    return {"process": process.to_dict()}


@app.post("/admin/purge")
@authorize
async def purge_old(db: Session = Depends(get_db), Authorization: Union[str, None] = Header(default=None)):
    """Remove satellites that have not been updated in two weeks"""

    utc_cutoff = (datetime.utcnow() - timedelta(days=14)).isoformat()

    # Find satellites
    satellites = db.query(models.Satellite).filter(
        models.Satellite.epoch < utc_cutoff).all()
    deletes = [satellite.to_dict()["satellite_name"]
               for satellite in satellites]

    # Delete satellites
    satellites = db.query(models.Satellite).filter(
        models.Satellite.epoch < utc_cutoff).delete()
    db.commit()

    return {"deleted": deletes}


@app.post("/graphql/")
async def graphql_fn(req: Request):
    """GraphQL default endpoint routing"""
    data = await req.json()  # JSON request data
    #request_json = data.decode('ascii')
    #print(data)
    _, result = graphql_sync(
        schema,
        data,
        context_value=data,
        debug=app.debug
    )
    #status_code = 200 if success else 400
    return result


# uvicorn main:app --reload
