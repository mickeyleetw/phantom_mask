from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, String,DateTime,Float
from sqlalchemy.ext.associationproxy import association_proxy

from settings.database import Base


class User(Base):
    __tablename__ = 'user'
    
    name = Column('name', String,unique=True)
    cash_balance = Column('cash_balance', Float)
    
    user_purchase_histories = relationship('UserPurchaseHistory', back_populates='user', cascade='all, delete-orphan')
    pharmacy_masks = association_proxy('user_purchase_histories', 'pharmacy_mask_price')
    
    

class UserPurchaseHistory(Base):
    __tablename__ = 'user_purchase_history'
    
    user_id = Column('user_id', Integer, ForeignKey('user.id'),index=True,nullable=False)
    user= relationship('User', foreign_keys=[user_id])
    
    pharmacy_mask_price_id= Column('pharmacy_mask_price_id', Integer, ForeignKey('pharmacy_mask_price.id'),index=True,nullable=False)
    pharmacy_mask_price= relationship('PharmacyMaskPrice', foreign_keys=[pharmacy_mask_price_id])
    transaction_date = Column('transaction_date', DateTime, nullable=False)
    transaction_amount = Column('transaction_amount', Float, nullable=False)