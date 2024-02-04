import abc
from typing import Optional
from decimal import Decimal
from sqlalchemy import cast, func,distinct

from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists, select,and_

from models.purchase_record import FilterPurchaseRecordsModel, PurchaseRecordModel
from settings.database import AsyncSession
from schemas.user import UserPurchaseHistory
from schemas.pharmacy import PharmacyMaskPrice,Mask


class AbstractPurchaseRecordRepository(abc.ABC):

    
    @abc.abstractmethod
    async def get_purchase_records(self,filter_: Optional[FilterPurchaseRecordsModel] = None) -> PurchaseRecordModel:
        raise NotImplementedError
    
    


class RDBPurchaseRecordRepository(AbstractPurchaseRecordRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @staticmethod   
    def _convert_purchase_record_to_model(amount_sum:Decimal,mask_sum:Optional[int]) -> PurchaseRecordModel:
        return PurchaseRecordModel(
            transaction_amount_sum=amount_sum,
            mask_amount_sum=mask_sum
        )
    
    async def get_purchase_records(self,filter_: Optional[FilterPurchaseRecordsModel] = None) -> PurchaseRecordModel:
        amount_stmt=select(func.sum(UserPurchaseHistory.transaction_amount))
        mask_stmt=select(func.count(distinct(PharmacyMaskPrice.mask_id))).join(UserPurchaseHistory,PharmacyMaskPrice.id == UserPurchaseHistory.pharmacy_mask_price_id)
        if filter_:
            if filter_.transaction_start_date:
                amount_stmt = amount_stmt.filter(UserPurchaseHistory.transaction_date >= filter_.transaction_start_date)
                mask_stmt=mask_stmt.filter(UserPurchaseHistory.transaction_date >= filter_.transaction_start_date)
            if filter_.transaction_end_date:
                amount_stmt = amount_stmt.filter(UserPurchaseHistory.transaction_date <= filter_.transaction_end_date)
                mask_stmt=mask_stmt.filter(UserPurchaseHistory.transaction_date <= filter_.transaction_end_date)
        
        amount_sum=(await self.session.execute(amount_stmt)).scalars().one()
        mask_sum=(await self.session.execute(mask_stmt)).scalars().one()
        
        return self._convert_purchase_record_to_model(amount_sum=amount_sum,mask_sum=mask_sum)
        