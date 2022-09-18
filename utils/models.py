from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from . database import Base

class Satellite(Base):
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

    def to_dict(self):
        values = {}
        for col in self.__table__.columns: # for each column in this object's __table__ attribute
            values[col.name] = getattr(self, col.name) # Get the object's value (pulls from db)
        return values
    