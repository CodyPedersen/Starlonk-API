from utils.models import Satellite, Process, Prediction
from utils.database import *
from datetime import datetime, timedelta
from utils.predict import predict_location

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


def satellite_prediction_resolver(obj, info, satellite_id, prediction_epoch):
    db = SessionLocal()

    try:
        satellite = db.query(Satellite).filter(Satellite.satellite_id == satellite_id).first()
        satellite_prediction = predict_location(satellite, prediction_epoch)
        payload = {
            "success" : True,
            "reference": satellite_prediction['reference'],
            "prediction": satellite_prediction['prediction']
        }
    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(e)}"]
        }
    print(payload)
    db.close()
    return payload


def bulk_prediction_resolver(obj, info, prediction_epoch):
    db = SessionLocal()

    try:
        all_satellites = db.query(Satellite).all()

        # Get location prediction for all satellites
        satellite_predictions = []
        for satellite in all_satellites:
            satellite_prediction = predict_location(satellite, prediction_epoch)
            satellite_predictions.append(satellite_prediction)
        
        payload = {
            "success" : True,
            "prediction": satellite_predictions
        }
        #print(satellite_prediction)
    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(e)}"]
        }

    db.close()
    return payload

def predict_next_n_resolver(obj, info, satellite_id, minutes):
    """Predicts next n minutes for a given satellite"""
    print("in predict_next_n")
    db = SessionLocal()
    time_cutoff = datetime.utcnow() + timedelta(minutes=minutes)
    prediction_list = []
    try:
        satellite_data = db.query(Satellite).filter(Satellite.satellite_id == satellite_id).first()
        print(satellite_data.to_dict())
        satellite_predictions = db.query(Prediction).filter(
            Prediction.satellite_id == satellite_id and
            Prediction.epoch <= time_cutoff and
            Prediction.epoch >= (datetime.utcnow() - timedelta(minutes=1))
        ).order_by(asc(Prediction.epoch)).all()

        for prediction in satellite_predictions:
            prediction_list.append(prediction.to_dict())

        payload = {
            "reference": satellite_data.to_dict(),
            "predictions": prediction_list,
            "success": True
        }
        
    except Exception as e:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve predictions: {str(e)}"]
        }
    return payload
