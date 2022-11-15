from utils.models import Satellite
from utils.database import *

#@query.field("satellite_by_id")
def satellite_by_id_resolver(obj, info, satellite_id):

    db = SessionLocal() # Can't use the FastAPI get_db - using SessionLocal() directly
    try:
        satellite = db.query(Satellite).filter(Satellite.satellite_id == satellite_id).first()
        payload = {
            "success": True,
            "satellite": satellite.to_dict()
        }
    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": ["Satellite item matching {id} not found"]
        }
    db.close()
    return payload

#@query.field("satellites")
def satellites_resolver(obj, info):
    db = SessionLocal()
    print('obj: ', obj)
    print('info: ', info, type(info))
    try:
        satellites = db.query(Satellite).all()
        payload = {
            "success" : True,
            "satellites": [satellite.to_dict() for satellite in satellites]
        }
    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve satellites: {str(e)} "]
        }

    db.close()
    return payload