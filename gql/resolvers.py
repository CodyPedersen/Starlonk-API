"""Resolvers for GraphQL operations"""
from datetime import datetime, timedelta

from database.database import *
from database.models import Satellite, Process, Prediction
from utils.predict import predict_location

#@query.field("satellite_by_id")
def satellite_by_id_resolver(obj, info, satellite_id):
    """Pull satellite data by id"""

    db = SessionLocal() # Can't use the FastAPI get_db - using SessionLocal() directly
    try:
        satellite = db.query(Satellite).filter(Satellite.satellite_id == satellite_id).first()
        payload = {
            "success": True,
            "satellite": satellite.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": ["Satellite item matching {id} not found"]
        }
    db.close()
    return payload


def satellites_resolver(obj, info):
    """Pull multiple satellites"""
    db = SessionLocal()

    try:
        satellites = db.query(Satellite).all()
        payload = {
            "success" : True,
            "satellites": [satellite.to_dict() for satellite in satellites]
        }
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve satellites: {str(ex)} "]
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
    except Exception as ex:  # TODO: not found
        payload = {
            "success": False,
            "errors": ["Process item matching {id} not found", str(ex)]
        }

    db.close()
    return payload

def processes_resolver(obj, info):
    """Get multiple processes"""
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
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(ex)}"]
        }

    db.close()
    return payload


def satellite_prediction_resolver(obj, info, satellite_id, prediction_epoch):
    """Predict the location of a given satellite"""
    db = SessionLocal()

    try:
        satellite = db.query(Satellite).filter(Satellite.satellite_id == satellite_id).first()
        satellite_prediction = predict_location(satellite, prediction_epoch)
        payload = {
            "success" : True,
            "reference": satellite_prediction['reference'],
            "prediction": satellite_prediction['prediction']
        }
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(ex)}"]
        }
    print(payload)
    db.close()
    return payload


def bulk_prediction_resolver(obj, info, prediction_epoch):
    """Predict the location of multiple satellites"""
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
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(ex)}"]
        }

    db.close()
    return payload

def predict_next_n_resolver(obj, info, satellite_id, minutes):
    """Predicts next n minutes for a given satellite"""
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
        
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve predictions: {str(ex)}"]
        }
    return payload


def bulk_predict_next_n_resolver(obj, info, minutes):
    """Bulk predict for next n minutes"""
    db = SessionLocal()
    time_cutoff = datetime.utcnow() + timedelta(minutes=minutes)

    prediction_ref_list = []
    try:
        all_satellites = db.query(Satellite).all()


        # Get location prediction for all satellites
        for satellite in all_satellites:
            satellite_predictions = []
            satellite_dict = satellite.to_dict()

            # Grab predictions for a given satellite
            satellite_prediction = db.query(Prediction).filter(
                Prediction.satellite_id == satellite_dict['satellite_id'] and
                Prediction.epoch <= time_cutoff and
                Prediction.epoch >= (datetime.utcnow() - timedelta(minutes=1))
            ).order_by(asc(Prediction.epoch)).all()

            for prediction in satellite_prediction:
                satellite_predictions.append(prediction.to_dict())

            sat_payload = {
                "reference": satellite_dict,
                "predictions": satellite_predictions
            }
            
            prediction_ref_list.append(sat_payload)

        
        payload = {
            "success" : True,
            "predictions": prediction_ref_list
        }
        #print(satellite_prediction)
    except Exception as ex:
        payload = {
            "success": False,
            "errors": [f"Unable to retrieve processes: {str(ex)}"]
        }

    db.close()
    return payload