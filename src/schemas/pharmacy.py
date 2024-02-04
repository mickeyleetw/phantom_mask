from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, String, Float
from sqlalchemy.ext.associationproxy import association_proxy

from settings.database import Base


class Pharmacy(Base):
    __tablename__ = 'pharmacy'

    name = Column('name', String,unique=True,index=True,nullable=False)
    cash_balance = Column('cash_balance', Float,nullable=False)

    pharmacy_mask_prices = relationship(
        'PharmacyMaskPrice', back_populates='pharmacy', cascade='all, delete-orphan'
    )
    masks = association_proxy('pharmacy_mask_prices', 'mask')
    
    pharmacy_business_times = relationship(
        'PharmacyBusinessTime', back_populates='pharmacy', cascade='all, delete-orphan'
    )
    business_times = association_proxy('pharmacy_business_times', 'business_times')


class Mask(Base):
    __tablename__ = 'mask'

    name = Column('name', String,unique=True,nullable=False)
    pharmacy_mask_prices = relationship(
        'PharmacyMaskPrice', back_populates='mask', cascade='all, delete-orphan'
    )
    pharmacies = association_proxy('pharmacy_mask_prices', 'pharmacy')
    

class PharmacyMaskPrice(Base):
    __tablename__ = 'pharmacy_mask_price'
    
    pharmacy_id = Column('pharmacy_id', Integer, ForeignKey('pharmacy.id'),index=True,nullable=False)
    pharmacy = relationship('Pharmacy', foreign_keys=[pharmacy_id],lazy="select")
    
    mask_id = Column('mask_id', Integer, ForeignKey('mask.id'),index=True,nullable=False)
    mask= relationship('Mask', foreign_keys=[mask_id],lazy="select")
    pharmacy_mask_price = Column('pharmacy_mask_price', Float,nullable=False)

