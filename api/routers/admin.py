import uuid
from datetime import datetime, timedelta
from typing import Union

from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session  # type: ignore


from api.auth import authorize
from utils.data import refresh_satellite_data
from database.database import get_db
from database import models

adm_router = APIRouter()


@adm_router.post("/admin/refresh/", status_code=202)
@authorize
async def refresh_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    Authorization: Union[str, None] = Header(default=None)
):
    """Pull data from NORAD data sets and update DB with data"""

    pid = str(uuid.uuid4())
    background_tasks.add_task(refresh_satellite_data, db, pid)

    return {
        "status": "accepted",
        "pid": pid
    }


@adm_router.get("/admin/process/{process_id}")
@authorize
async def get_process(
    process_id,
    db: Session = Depends(get_db),
    Authorization: Union[str, None] = Header(default=None)
):
    """Get the status given process (refresh)"""

    process = db.query(models.Process).filter(
        models.Process.id == process_id).first()

    if not process:
        return {"process": []}
    
    return {"process": process.one().to_dict()}


@adm_router.post("/admin/purge")
@authorize
async def purge_old(
    db: Session = Depends(get_db), Authorization: Union[str, None] = Header(default=None)
):
    """Remove satellites that have not been updated in two weeks"""

    utc_cutoff = (datetime.utcnow() - timedelta(days=14)).isoformat()

    # Find satellites
    satellites = db.query(models.Satellite).filter(
        models.Satellite.epoch < utc_cutoff).all()
    deletes = [satellite.to_dict()["satellite_name"]
               for satellite in satellites]

    # Delete satellites
    satellites = db.query(models.Satellite).filter(
        models.Satellite.epoch < utc_cutoff).delete()
    db.commit()

    return {"deleted": deletes}
