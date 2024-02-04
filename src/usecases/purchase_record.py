from typing import Optional
from datetime import datetime
from decimal import Decimal

from core.enum import DayOfTheWeekEnum,PharmacyMaskOrderByEnum
from core.exception import ResourceNotFoundException
from dependency_injections import async_unit_of_work
from models.purchase_record import PurchaseRecordModel,FilterPurchaseRecordsModel


class PurchaseRecordUsecase:
    
    @staticmethod
    async def get_purchase_records(
        transaction_start_date: Optional[datetime],
        transaction_end_date: Optional[datetime],
    ) -> PurchaseRecordModel:
        async with async_unit_of_work() as auow:
            filter_ = FilterPurchaseRecordsModel(
                transaction_end_date=transaction_end_date,
                transaction_start_date=transaction_start_date
            )

            return await auow.purchase_record_repo.get_purchase_records(filter_)