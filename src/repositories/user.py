import abc
from typing import Optional
from sqlalchemy import func
from decimal import Decimal

from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists, select,and_,or_
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from schemas.user import User, UserPurchaseHistory
from schemas.pharmacy import PharmacyMaskPrice
from models.user import UserModel,FilterUserParamsModel,UserPurchaseHistoryModel,CreateUserPurchaseHistoryModel
from settings.database import AsyncSession

class AbstractUserRepository(abc.ABC):
    
    @abc.abstractmethod
    async def get_users(
        self,
        filter_: Optional[FilterUserParamsModel] = None,
    ) -> list[UserModel]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def is_user_existed(self, user_id: int) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user_purchase_history(self, user_id:int,transaction_amount:Decimal,mask_pharmacy_id:int)->int:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def update_user_balance(self,user_id:int,transaction_amount:Decimal)->None:
        raise NotImplementedError


class RDBUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @staticmethod
    def _convert_user_purchase_history_schema_to_model(purchase_history:UserPurchaseHistory)->UserPurchaseHistoryModel:
        return UserPurchaseHistoryModel(
            id=purchase_history.id,
            pharmacy_name=purchase_history.pharmacy_mask_price.pharmacy.name,
            mask_name=purchase_history.pharmacy_mask_price.mask.name,
            transaction_amount=purchase_history.transaction_amount,
            transaction_date=purchase_history.transaction_date
        )
    
    def _convert_user_schema_to_model(self,user:User) -> UserModel:
        return UserModel(
            id=user.id,
            name=user.name,
            purchase_histories=list(map(self._convert_user_purchase_history_schema_to_model,user.user_purchase_histories))
        )
    
    async def is_user_existed(self, user_id: int) -> bool:
        stmt = select(exists(select(User).filter_by(id= user_id)))
        return (await self.session.execute(stmt)).scalars().one()

    async def get_users(
        self,
        filter_: Optional[FilterUserParamsModel] = None,
    ) -> list[UserModel]:
        stmt = select(User).join(UserPurchaseHistory,User.id == UserPurchaseHistory.user_id).group_by(User.id)\
            .options(selectinload(User.user_purchase_histories).selectinload(UserPurchaseHistory.pharmacy_mask_price).selectinload(PharmacyMaskPrice.pharmacy),
                     selectinload(User.user_purchase_histories).selectinload(UserPurchaseHistory.pharmacy_mask_price).selectinload(PharmacyMaskPrice.mask),)
        if filter_:
            if filter_.transaction_date_interval:
                start_date,end_date = filter_.transaction_date_interval
                if start_date:
                    stmt = stmt.where(UserPurchaseHistory.transaction_date >= start_date)
                if end_date:
                    stmt = stmt.where(UserPurchaseHistory.transaction_date <= end_date)
            if filter_.ascending:
                stmt = stmt.order_by(func.sum(UserPurchaseHistory.transaction_amount).asc())
            else:
                stmt = stmt.order_by(func.sum(UserPurchaseHistory.transaction_amount).desc())
            if filter_.limit:
                stmt = stmt.limit(filter_.limit)
        
        users=(await self.session.execute(stmt)).scalars().all()
    
        return list(map(self._convert_user_schema_to_model, users))
    
    async def create_user_purchase_history(self, user_id:int,transaction_amount:Decimal,mask_pharmacy_id:int)->int:
        new_history = UserPurchaseHistory(
            user_id=user_id,
            pharmacy_mask_price_id=mask_pharmacy_id,
            transaction_date=datetime.now(),
            transaction_amount=transaction_amount
        )
        self.session.add(new_history)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise e

        return new_history.id
    
    async def update_user_balance(self,user_id:int,transaction_amount:Decimal)->None:
        stmt = select(User).filter_by(id=user_id).with_for_update()
        user = (await self.session.execute(stmt)).scalars().one()
        cash_balance=Decimal(user.cash_balance) 
        cash_balance-= transaction_amount
        if cash_balance<0:
            raise ValueError("User cash balance cannot be negative")
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise e