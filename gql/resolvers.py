from utils.models import Satellite, Process
from utils.database import *
from datetime import datetime

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

def process_by_id_resolver(obj, info, process_id):

    db = SessionLocal() # Can't use the FastAPI get_db - using SessionLocal() directly
    try:
        process = db.query(Process).filter(Process.id == process_id).first()
        process_dict = process.to_dict()

        process_dict['time_created'] = process_dict['time_created'].isoformat()
        process_dict['time_updated'] = process_dict['time_updated'].isoformat()

        payload = {
            "success": True,
            "process": process_dict
        }
    except Exception as e:  # todo not found
        payload = {
            "success": False,
            "errors": ["Process item matching {id} not found", str(e)]
        }

    db.close()
    return payload

def processes_resolver(obj, info):
    db = SessionLocal()

    try:
        processes_dt = db.query(Process).all()
        #print(processes_dt)

        processes = []
        for process_obj in processes_dt:
            process_dict = process_obj.to_dict()

            process_dict['time_created'] = process_dict['time_created'].isoformat()
            process_dict['time_updated'] = process_dict['time_updated'].isoformat()

            processes.append(process_dict)

        payload = {
            "success" : True,
            "processes": processes
        }
    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(e)}"]
        }

    db.close()
    return payload