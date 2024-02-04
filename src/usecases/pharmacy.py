from typing import Optional
from datetime import time
from decimal import Decimal

from core.enum import DayOfTheWeekEnum,PharmacyMaskOrderByEnum
from core.exception import ResourceNotFoundException
from dependency_injections import async_unit_of_work
from models.pharmacy import FilterPharmacyParamsModel,PharmacyModel,FilterPharmacyMaskParamsModel


class PharmacyUsecase:
    
    @staticmethod
    async def get_pharmacies(
        offset: Optional[int],
        limit: Optional[int],
        time: Optional[time],
        name: Optional[str],
        order_by: Optional[PharmacyMaskOrderByEnum],
        ascending: Optional[bool],
        day_of_the_week: Optional[DayOfTheWeekEnum],
        mask_price_upper_bound: Optional[Decimal],
        mask_price_lower_bound: Optional[Decimal],
        mask_type_count: Optional[int],
        greater_than:Optional[bool]
    ) -> list[PharmacyModel]:
        async with async_unit_of_work() as auow:
            filter_ = FilterPharmacyParamsModel(
                name=name,
                order_by=order_by,
                ascending=ascending,
                pagination=(offset, limit),
                open_time=(time,day_of_the_week),
                mask_type_condition=(mask_type_count,greater_than),
                mask_price_interval=(mask_price_lower_bound,mask_price_upper_bound),
            )

            return await auow.pharmacy_repo.get_pharmacies(filter_)
    
    
    @staticmethod
    async def get_pharmacy_masks(
        pharmacy_name:str,
        offset: Optional[int],
        limit: Optional[int],
        order_by: Optional[PharmacyMaskOrderByEnum],
        ascending: Optional[bool],
    ) -> list[PharmacyModel]:
        async with async_unit_of_work() as auow:
            if not await auow.pharmacy_repo.is_pharmacy_existed(pharmacy_name=pharmacy_name):
                raise ResourceNotFoundException('Pharmacy')

            filter_ = FilterPharmacyMaskParamsModel(
                pagination=(offset, limit), order_by=order_by, ascending=ascending
            )

            return await auow.pharmacy_repo.get_pharmacy_masks(pharmacy_name=pharmacy_name,filter_=filter_)

