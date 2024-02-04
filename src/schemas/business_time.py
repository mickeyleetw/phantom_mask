from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, String,Time
from sqlalchemy.ext.associationproxy import association_proxy

from settings.database import Base


class BusinessDay(Base):
    __tablename__ = 'business_day'

    name = Column('name', String,unique=True)


class PharmacyBusinessTime(Base):
    __tablename__ = 'pharmacy_business_time'
    
    pharmacy_id = Column('pharmacy_id', Integer, ForeignKey('pharmacy.id'),index=True,nullable=False)
    pharmacy = relationship('Pharmacy', foreign_keys=[pharmacy_id])
    
    business_day_id = Column('business_day_id', Integer, ForeignKey('business_day.id'),index=True,nullable=False)
    business_day= relationship('BusinessDay', foreign_keys=[business_day_id])
    open_time = Column('open_time', Time,nullable=False)
    close_time = Column('close_time', Time,nullable=False)