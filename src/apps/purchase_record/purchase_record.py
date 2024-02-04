from fastapi import APIRouter
from starlette import status
from typing import Optional
from decimal import Decimal


from core.fastapi import APIRoute
from core.response import default_responses
from core.pydantic import ParameterInt,ParameterDate
from models.purchase_record import PurchaseRecordModel
from usecases.purchase_record import PurchaseRecordUsecase



router = APIRouter(
    prefix='/purchase-records',
    tags=['Purchase Record'],
    responses=default_responses,
    route_class=APIRoute
)


@router.get(
    '/summary' ,
    response_model=PurchaseRecordModel,
    status_code=status.HTTP_200_OK,)
async def get_users(
    transaction_start_date: Optional[ParameterDate] = None,
    transaction_end_date: Optional[ParameterDate] = None,
) -> PurchaseRecordModel:
    return await PurchaseRecordUsecase.get_purchase_records(
        transaction_start_date=transaction_start_date,
        transaction_end_date=transaction_end_date,
    )