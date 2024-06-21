from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session  # type: ignore

from api.schema.satellites import SatelliteQuery
from database.database import get_db
import database.models as models
import utils.predict as predict


sat_router = APIRouter()

@sat_router.get("/satellites/")
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


@sat_router.get("/predict/")
async def predict_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    """Predict the location of a single satellite for a given epoch"""

    param_dict = params.dict(exclude_none=True)
    satellite_id = param_dict.get('satellite_id')

    if not satellite_id:
        err = "Must provide a valid satellite id"
        raise ValueError(err)

    epoch = param_dict.get('epoch')
    if not epoch:
        err = "Must provide a valid epoch"
        raise ValueError(err)

    # Get satellite
    satellite = db.query(models.Satellite).filter(
        models.Satellite.satellite_id == satellite_id).first()

    satellite_prediction = predict.predict_location(satellite, epoch)

    return satellite_prediction


@sat_router.get("/bulk_predict/")
async def get_bulk_satellites(db: Session = Depends(get_db), params: SatelliteQuery = Depends()):
    """Predict all satellite location for a given epoch"""

    param_dict = params.dict(exclude_none=True)

    epoch = param_dict.get('epoch')

    if not epoch:
        err = "Epoch must be defined for a bulk prediction"
        raise ValueError(err)

    # Get all satellites in DB
    all_satellites = db.query(models.Satellite).all()

    # Get location prediction for all satellites
    satellite_predictions = []
    for satellite in all_satellites:
        satellite_prediction = predict.predict_location(satellite, epoch)
        satellite_predictions.append(satellite_prediction)

    return {"satellites": satellite_predictions}