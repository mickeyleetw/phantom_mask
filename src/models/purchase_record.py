from core.pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal



class PurchaseRecordModel(BaseModel):
    mask_amount_sum: int
    transaction_amount_sum:Decimal


class FilterPurchaseRecordsModel(BaseModel):
    transaction_start_date: Optional[datetime]
    transaction_end_date: Optional[datetime]