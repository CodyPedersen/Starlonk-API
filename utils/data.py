import requests
from utils.models import Satellite, Process
from sqlalchemy.orm import Session

from utils.log_util import log_data
import traceback


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

        # Modify keys to Satellite model standards
        satellite = {
            key.replace('OBJECT', 'satellite').lower():value for (key,value) in raw_satellite.items()
        }
        del satellite['mean_motion_ddot']
        satellite['source'] = source

        # Push `clean` satellite to `cleaned_data`
        satellites.append(satellite)

    return satellites


def pull_satellite_data() -> list:

    # Pull STARLINK satellites
    starlink = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json-pretty'
    
    log_data("Pulling data from NORAD")
    try:
        satellite_response = requests.get(url=starlink)
        log_data(f"satellite_response{satellite_response}")
    except:
        log_data("Unable to complete request")
        log_data(traceback.print_exc())

    log_data("Parsing data from NORAD")
    try:
        raw_data = satellite_response.json()
    except:
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
    satellite_data = format_satellite_data(raw_data, source='STARLINK')
    #log_data(f"About to parse satellite data {satellite_data}")

    # Unpack and create object for each satellite
    satellites_to_add = []
    for satellite_json in satellite_data:

        updated = False
        updated = db.query(Satellite).filter(Satellite.satellite_id == satellite_json['satellite_id']).update(satellite_json)
        db.commit()

        if not updated:
            satellite = Satellite(**satellite_json)
            satellites_to_add.append(satellite)

    db.add_all(satellites_to_add)
    db.commit()
    push_process(db, pid, "complete")