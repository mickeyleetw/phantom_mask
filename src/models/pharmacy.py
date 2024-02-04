from core.pydantic import BaseModel
from typing import Optional
from datetime import time
from decimal import Decimal

from core.enum import DayOfTheWeekEnum,PharmacyMaskOrderByEnum,PharmacyOrderByEnum

class FilterPharmacyParamsModel(BaseModel):
    name: Optional[str]
    order_by: Optional[PharmacyOrderByEnum] = None
    ascending: Optional[bool] = True
    pagination: Optional[tuple[int, Optional[int]]] = None
    open_time: Optional[tuple[Optional[time],Optional[DayOfTheWeekEnum]]] = None
    mask_type_condition: Optional[tuple[Optional[int],Optional[bool]]] = None
    mask_price_interval: Optional[tuple[Optional[Decimal],Optional[Decimal]]] = None


class FilterPharmacyMaskParamsModel(BaseModel):
    pagination: Optional[tuple[int, Optional[int]]] = None
    order_by: Optional[PharmacyMaskOrderByEnum] = None
    ascending: Optional[bool] = True

class PharmacyMaskModel(BaseModel):
    id:int
    name: str
    price:Decimal
    

class PharmacyBusinessTimeModel(BaseModel):
    id: int
    business_day: DayOfTheWeekEnum
    open_time: time
    close_time: time

class PharmacyModel(BaseModel):
    id: int
    name: str
    business_times: list[PharmacyBusinessTimeModel]
    masks: list[PharmacyMaskModel]

