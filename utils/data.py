"""Data ETL Processes"""
import logging

import requests
from sqlalchemy.orm import Session

from utils.models import Satellite, Process


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs.txt',
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)


def push_process(db: Session, pid: str, status: str):
    """Pushes processes to database"""
    print("pushing process to db")
    
    # Create a new Process instance with the given data
    process = Process(id=pid, status=status)

    db.merge(process)
    print("pushed process to db")


def format_satellite_data(satellite_json: list, source: str) -> list:
    """Formats satellite JSON formats to a more user-friendly alternative"""
    satellites = []

    # Change satellite keys to a more readable format
    for raw_satellite in satellite_json:

        # Modify keys to Satellite model standards
        satellite = {
            key.replace('OBJECT', 'satellite').lower():value 
            for (key,value) in raw_satellite.items()
        }
        del satellite['mean_motion_ddot']
        satellite['source'] = source

        # Push `clean` satellite to `cleaned_data`
        satellites.append(satellite)

    return satellites


def pull_satellite_data() -> list:
    """Pull NORAD Satellite data"""
    # Pull STARLINK satellites
    starlink = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json-pretty'
    
    logging.info("Pulling data from NORAD")
    try:
        satellite_response = requests.get(url=starlink, timeout=None)
        logging.info(f"satellite_response{satellite_response}")
    except Exception as e:
        logging.error(f"Unable to complete NORAD request: {repr(e)}")
        raise e

    logging.info("Parsing data from NORAD")
    try:
        raw_data = satellite_response.json()
    except Exception as e:
        logging.error(f"Failed to parse json: {repr(e)}")
        raise e

    return raw_data


async def refresh_satellite_data(db: Session, pid: str) -> None:
    ''' Pulls Satellite data from Gov. sources, cleans it and pushes it to the DB '''

    # Create Process and push to DB
    push_process(db, pid, status="started")

    # Begin satellite data ETL
    raw_data = pull_satellite_data()
    satellite_data = format_satellite_data(raw_data, source='STARLINK')

    # Unpack and create object for each satellite
    satellites_to_add = []
    for satellite_json in satellite_data:

        updated = False
        updated = db.query(Satellite).filter(
                Satellite.satellite_id == satellite_json['satellite_id']
            ).update(satellite_json)
        db.commit()

        if not updated:
            satellite = Satellite(**satellite_json)
            satellites_to_add.append(satellite)

    db.add_all(satellites_to_add)
    db.commit()
    push_process(db, pid, "complete")
    