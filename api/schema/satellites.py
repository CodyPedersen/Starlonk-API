"""REST response schemas"""
from typing import Optional
from pydantic import BaseModel


class SatelliteQuery(BaseModel):
    """Schema for satellite queries"""
    
    satellite_name: Optional[str]
    satellite_id: Optional[str]
    epoch: Optional[str]
    mean_motion: Optional[float]
    eccentricity: Optional[float]
    inclination: Optional[float]
    ra_of_asc_node: Optional[float]
    arg_of_pericenter: Optional[float]
    mean_anomaly: Optional[float]
    ephemeris_type: Optional[int]
    classification_type: Optional[str]
    norad_cat_id: Optional[int]
    element_set_no: Optional[int]
    rev_at_epoch: Optional[int]
    bstar: Optional[float]
    mean_motion_dot: Optional[float]
    source: Optional[str]
