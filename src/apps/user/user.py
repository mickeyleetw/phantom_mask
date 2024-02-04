from fastapi import APIRouter
from starlette import status
from typing import Optional

from core.fastapi import APIRoute
from core.response import default_responses
from core.pydantic import ParameterInt,ParameterDate
from models.user import UserModel,CreateUserPurchaseHistoryModel
from usecases.user import UserUsecase
from core.response import response_201,response_404


router = APIRouter(
    prefix='/users',
    tags=['User'],
    responses=default_responses,
    route_class=APIRoute
)


@router.get(
    '', 
    response_model=list[UserModel],
    status_code=status.HTTP_200_OK,)
async def get_users(
    limit: Optional[ParameterInt] = None,
    transaction_start_date: Optional[ParameterDate] = None,
    transaction_end_date: Optional[ParameterDate] = None,
    ascending: Optional[bool] = False,
) -> list[UserModel]:
    return await UserUsecase.get_users(
        limit=limit,
        transaction_start_date=transaction_start_date,
        transaction_end_date=transaction_end_date,
        ascending=ascending
    )

@router.post(
    '/{user_id}/mask', 
    status_code=status.HTTP_201_CREATED,
    responses={
        **response_201(CreateUserPurchaseHistoryModel, 'UserPurchaseHistory'),
        **response_404('User or Pharmacy Mask relation'),
    },
    )
async def create_user_purchase_history(
    user_id: int,
    data: CreateUserPurchaseHistoryModel
) -> int:
    return await UserUsecase.create_user_purchase_history(
        user_id=user_id,
        data=data
    )