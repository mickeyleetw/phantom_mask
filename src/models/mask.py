from core.pydantic import BaseModel
from typing import Optional
from core.enum import MaskOrderByEnum

class MaskModel(BaseModel):
    id:int
    name: str
    

class FilterMaskParamsModel(BaseModel):
    name: Optional[str]
    order_by: Optional[MaskOrderByEnum] = None
    ascending: Optional[bool] = True