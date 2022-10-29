import requests
from utils.models import Satellite, Process
from sqlalchemy.orm import Session
# import logging
import traceback
from datetime import datetime

# logger = logging.getLogger(__name__)
# logging.basicConfig(format='Custom Logs: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def log_data(data):
    with open("log.txt", mode="a+") as logfile:
        try:
            logfile.write(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': ' + data + "\n")
        except:
            logfile.write("Failed to write\n")


def push_process(db : Session, pid: str, status: str):
    print("pushing process to db")
    process_data = {
        "id" : pid,
        "status" : status
    }

    # Query processes on pid
    exists = db.query(Process).filter(Process.id == pid)

    # Update value if exists, else create
    if exists.first():
        process_obj = exists.one()
        process_obj.status = status
        db.commit()
    else:
        process = Process(**process_data)
        db.add(process)

    
    db.commit()
    print("pushed process to db")


def format_satellite_data(satellite_json: list, source: str) -> list:
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


def pull_satellite_data() -> list:

    # Pull STARLINK satellites
    starlink = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json-pretty'
    
    log_data("1 from NORAD")
    print("Pulling data from NORAD")
    try:
        satellite_response = requests.get(url=starlink)
        log_data(f"satellite_response{satellite_response}")
    except:
        log_data("Unable to complete request")

        log_data(traceback.print_exc())
        log_data(traceback.print_exception())

    log_data("Parsing data from NORAD")
    print("Parsing data from NORAD")
    try:
        raw_data = satellite_response.json()
    except:
        log_data("Unable to parse response")
        log_data(traceback.print_exc())
        log_data(traceback.print_exception())

    # Pull Military satellites
    
    # Pull NOAA satellites

    return raw_data


async def refresh_satellite_data(db: Session, pid: str) -> None:
    ''' Pulls Satellite data from Gov. sources, cleans it and pushes it to the DB '''

    # Create Process and push to DB
    push_process(db, pid, status="started")

    # Begin satellite data ETL
    raw_data = pull_satellite_data()
    satellite_data = format_satellite_data(raw_data, 'STARLINK')
    log_data(f"About to parse satellite data {satellite_data}")

    # Unpack and create object for each satellite
    satellites_to_add = []
    for satellite_json in satellite_data:

        updated = False
        updated = db.query(Satellite).filter(Satellite.satellite_id == satellite_json['satellite_id']).update(satellite_json)
        db.commit()

        if not updated:
            satellite = Satellite(**satellite_json)
            satellites_to_add.append(satellite)

    log_data("About to add satellite data")
    db.add_all(satellites_to_add)
    log_data("About to commit satellite data")
    db.commit()
    push_process(db, pid, "complete")