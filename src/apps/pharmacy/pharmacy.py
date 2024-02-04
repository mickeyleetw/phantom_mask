from fastapi import APIRouter
from starlette import status
from typing import Optional
from decimal import Decimal


from core.fastapi import APIRoute
from core.response import default_responses
from core.pydantic import ParameterInt,ParameterTime
from core.enum import DayOfTheWeekEnum,PharmacyMaskOrderByEnum,PharmacyOrderByEnum
from models.pharmacy import PharmacyModel,PharmacyMaskModel
from usecases.pharmacy import PharmacyUsecase



router = APIRouter(
    prefix='/pharmacies',
    tags=['Pharmacy'],
    responses=default_responses,
    route_class=APIRoute
)


@router.get(
    '', 
    response_model=list[PharmacyModel],
    status_code=status.HTTP_200_OK,)
async def get_pharmacies(
    offset: Optional[ParameterInt] = 0,
    limit: Optional[ParameterInt] = None,
    time: Optional[ParameterTime] = None,
    name: Optional[str] = None,
    order_by: Optional[PharmacyOrderByEnum] = None,
    ascending: Optional[bool] = True,
    day_of_the_week: Optional[DayOfTheWeekEnum] = DayOfTheWeekEnum.MONDAY,
    mask_price_upper_bound: Optional[Decimal] = None,
    mask_price_lower_bound: Optional[Decimal] = None,
    mask_type_count: Optional[int] = None,
    greater_than:Optional[bool] = False
) -> list[PharmacyModel]:
    return await PharmacyUsecase.get_pharmacies(
        offset=offset,
        limit=limit,
        name=name,
        time=time,
        order_by=order_by,
        ascending=ascending,
        day_of_the_week=day_of_the_week,
        mask_price_upper_bound=mask_price_upper_bound,
        mask_price_lower_bound=mask_price_lower_bound,
        mask_type_count=mask_type_count,
        greater_than=greater_than
    )

@router.get(
    '/{pharmacy_name}/masks', 
    response_model=list[PharmacyMaskModel],
    status_code=status.HTTP_200_OK,)
async def get_pharmacy_masks(
    pharmacy_name:str,
    offset: Optional[ParameterInt] = 0,
    limit: Optional[ParameterInt] = None,
    order_by: Optional[PharmacyMaskOrderByEnum] = PharmacyMaskOrderByEnum.NAME,
    ascending: Optional[bool] = False,
) -> list[PharmacyModel]:
    return await PharmacyUsecase.get_pharmacy_masks(
        pharmacy_name=pharmacy_name,
        offset=offset,
        limit=limit,
        order_by=order_by,
        ascending=ascending
    )
