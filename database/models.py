from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY
from sqlalchemy.sql import func

from .database import Base

class BaseObj(Base):

    __abstract__ = True
    def to_dict(self):
        """Convert attributes to a dictionary"""
        values = {}
        for col in self.__table__.columns: # for each column in this object's __table__ attribute
            values[col.name] = getattr(self, col.name) # Get the object's value (pulls from db)
        return values


class Satellite(BaseObj):
    """Satellite table, holds data NORAD data"""
    __tablename__ = "satellite"
    satellite_name = Column(String, index=True)
    satellite_id = Column(String, unique=True, primary_key = True)
    epoch = Column(String)
    mean_motion = Column(Float)
    eccentricity = Column(Float)
    inclination = Column(Float)
    ra_of_asc_node = Column(Float)
    arg_of_pericenter = Column(Float)
    mean_anomaly = Column(Float)
    ephemeris_type = Column(Integer)
    classification_type = Column(String)
    norad_cat_id = Column(Integer)
    element_set_no = Column(Integer)
    rev_at_epoch = Column(Integer)
    bstar =  Column(Float)
    mean_motion_dot = Column(Float)
    source = Column(String)


    

class Process(BaseObj):
    """Holds active and completed processes; updates, refreshes*"""
    __tablename__ = "process"
    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Prediction(BaseObj):
    """Holds data related to satellite prediction"""
    __tablename__ = "prediction"
    satellite_name = Column(String, index=True)
    satellite_id = Column(String, primary_key=True)
    epoch = Column(DateTime, primary_key=True)
    elevation = Column(Float)
    geocentric_coords = Column(ARRAY(Float))
    geo_velocity_m_per_s = Column(ARRAY(Float))
    latitude = Column(Float)
    longitude = Column(Float)

    