from core.pydantic import BaseModel,UTCDatetime
from decimal import Decimal
from typing import Optional
from datetime import datetime

class FilterUserParamsModel(BaseModel):
    limit: Optional[int] 
    ascending: Optional[bool] = True
    transaction_date_interval: Optional[tuple[Optional[datetime],Optional[datetime]]] = None


class UserPurchaseHistoryModel(BaseModel):
    id: int
    pharmacy_name: str
    mask_name: str
    transaction_amount: Decimal
    transaction_date: UTCDatetime


class UserModel(BaseModel):
    id: int
    name: str
    purchase_histories: list[UserPurchaseHistoryModel]


class CreateUserPurchaseHistoryModel(BaseModel):
    pharmacy_id: int
    mask_id: int
    transaction_amount: Decimal
    