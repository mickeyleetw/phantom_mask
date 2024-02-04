from fastapi import APIRouter
from starlette import status
from typing import Optional
from decimal import Decimal


from core.fastapi import APIRoute
from core.response import default_responses
from core.pydantic import ParameterInt,ParameterTime
from core.enum import MaskOrderByEnum
from models.mask import MaskModel
from usecases.mask import MaskUsecase

router = APIRouter(
    prefix='/masks',
    tags=['Mask'],
    responses=default_responses,
    route_class=APIRoute
)



@router.get(
    '', 
    response_model=list[MaskModel],
    status_code=status.HTTP_200_OK,)
async def get_masks(
    name:Optional[str]=None,
    order_by: Optional[MaskOrderByEnum] = MaskOrderByEnum.NAME,
    ascending: Optional[bool] = False,
) -> list[MaskModel]:
    return await MaskUsecase.get_masks(
        name=name,
        order_by=order_by,
        ascending=ascending
    )