from typing import Optional
from datetime import time
from decimal import Decimal

from core.enum import MaskOrderByEnum
from core.exception import ResourceNotFoundException
from dependency_injections import async_unit_of_work
from models.pharmacy import FilterPharmacyParamsModel,PharmacyModel,FilterPharmacyMaskParamsModel
from models.mask import FilterMaskParamsModel,MaskModel

class MaskUsecase:
    
    @staticmethod
    async def get_masks(
        name:str,
        order_by: Optional[MaskOrderByEnum],
        ascending: Optional[bool],
    ) -> list[MaskModel]:
        async with async_unit_of_work() as auow:

            filter_ = FilterMaskParamsModel(
                name=name, order_by=order_by, ascending=ascending
            )

            return await auow.mask_repo.get_masks(filter_=filter_)
