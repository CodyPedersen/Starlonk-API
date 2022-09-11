import requests
from models import Satellite
from sqlalchemy.orm import Session #probably not necessary
import json


def clean_satellite_data(satellite_json, source):
    satellites = []

    # Change satellite keys to a more readable format
    for raw_satellite in satellite_json:
        satellite = {}

        # Modify keys to Satellite model standards
        satellite['satellite_name'] = raw_satellite['OBJECT_NAME']
        satellite['satellite_id'] = raw_satellite['OBJECT_ID']
        satellite['epoch'] = raw_satellite['EPOCH']
        satellite['mean_motion'] = raw_satellite['MEAN_MOTION']
        satellite['eccentricity'] = raw_satellite['ECCENTRICITY']
        satellite['inclination'] = raw_satellite['INCLINATION']
        satellite['ra_of_asc_node'] = raw_satellite['RA_OF_ASC_NODE']
        satellite['arg_of_pericenter'] = raw_satellite['ARG_OF_PERICENTER']
        satellite['mean_anomaly'] = raw_satellite['MEAN_ANOMALY']
        satellite['ephemeris_type'] = raw_satellite['EPHEMERIS_TYPE']
        satellite['classification_type'] = raw_satellite['CLASSIFICATION_TYPE']
        satellite['norad_cat_id'] = raw_satellite['NORAD_CAT_ID']
        satellite['element_set_no'] = raw_satellite['ELEMENT_SET_NO']
        satellite['rev_at_epoch'] = raw_satellite['REV_AT_EPOCH']
        satellite['bstar'] =  float(raw_satellite['BSTAR'])
        satellite['mean_motion_dot'] = float(raw_satellite['MEAN_MOTION_DOT'])
        satellite['source'] = source

        # Push `clean` satellite to `cleaned_data`
        satellites.append(satellite)
    
    return satellites


def pull_satellite_data():

    # Pull STARLINK satellites
    starlink = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json-pretty'
    satellite_response = requests.get(url=starlink)
    raw_data = satellite_response.json()

    starlink_satellites = clean_satellite_data(raw_data, 'STARLINK')

    # Pull Military satellites
    
    # Pull NOAA satellites

    
    return starlink_satellites



def refresh_satellite_data(db: Session):
    satellite_data = pull_satellite_data()
    satellite_objects = []

    # Unpack and create object for each satellite
    for satellite_json in satellite_data:

        # Update value if it exists in DB already
        updated = db.query(Satellite).filter(Satellite.satellite_id == satellite_json['satellite_id']).update(satellite_json)
        
        # If successfully updated, remove the json object from satellite data 
        if updated:
            satellite_data.remove(satellite_json)
        else:
            satellite = Satellite(**satellite_json)
            satellite_objects.append(satellite)

    db.add_all(satellite_objects)
    db.commit()

#refresh_satellite_data()
