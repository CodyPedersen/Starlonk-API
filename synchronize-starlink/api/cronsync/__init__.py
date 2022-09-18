import logging
import datetime
import requests
import os

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    # Pull env. vars
    sync_url = os.environ["sync_url"]
    api_key = os.environ["api_key"]

    # Attempt to refresh data
    response = requests.post(url=sync_url, params={"api_key" : api_key})
    output_json = response.json()

    logging.info(output_json)

    logging.info(f"Update: {output_json.get('status', 'Failure')}")
    logging.info('Python timer trigger function ran at %s', utc_timestamp)