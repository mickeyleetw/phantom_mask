from typing import Optional
from datetime import datetime

from dependency_injections import async_unit_of_work
from core.exception import ResourceNotFoundException
from models.user import UserModel,FilterUserParamsModel,CreateUserPurchaseHistoryModel


class UserUsecase:
    
    @staticmethod
    async def get_users(
        limit: Optional[int],
        transaction_start_date: Optional[datetime],
        transaction_end_date: Optional[datetime],
        ascending: Optional[bool]
    ) -> list[UserModel]:
        async with async_unit_of_work() as auow:
            filter_ = FilterUserParamsModel(
                limit=limit,
                ascending=ascending,
                transaction_date_interval=(transaction_start_date,transaction_end_date),
            )

            return await auow.user_repo.get_users(filter_)
    # create_user_purchase_history
    
    @staticmethod
    async def create_user_purchase_history(
        user_id: int,
        data: CreateUserPurchaseHistoryModel
    ) -> int:
        async with async_unit_of_work() as auow:
            if not await auow.user_repo.is_user_existed(user_id=user_id):
                raise ResourceNotFoundException('User')
            
            mask_pharmacy_id=(await auow.pharmacy_repo.get_mask_pharmacy_relation_id(pharmacy_id=data.pharmacy_id,mask_id=data.mask_id))
            if not mask_pharmacy_id:
                raise ResourceNotFoundException('Pharmacy Mask relation')

            new_record_id= await auow.user_repo.create_user_purchase_history(user_id=user_id,transaction_amount=data.transaction_amount,mask_pharmacy_id=mask_pharmacy_id)
            await auow.user_repo.update_user_balance(user_id=user_id,transaction_amount=data.transaction_amount)
            return new_record_id