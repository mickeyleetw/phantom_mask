import abc
from typing import Optional
from sqlalchemy import cast, func
from sqlalchemy.types import DECIMAL


from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import exists, select,and_,or_

from schemas.pharmacy import Pharmacy, Mask, PharmacyMaskPrice
from schemas.business_time import PharmacyBusinessTime, BusinessDay
from models.pharmacy import FilterPharmacyParamsModel,PharmacyModel,PharmacyBusinessTimeModel,FilterPharmacyMaskParamsModel,PharmacyMaskModel
from settings.database import AsyncSession
from core.enum import PharmacyMaskOrderByEnum

class AbstractPharmacyRepository(abc.ABC):

    @abc.abstractmethod
    async def is_pharmacy_existed(self, pharmacy_name: str) -> bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_mask_pharmacy_relation_id(self, pharmacy_id: int,mask_id:int) -> bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_pharmacy_masks(self,pharmacy_name:str,filter_: Optional[FilterPharmacyMaskParamsModel] = None) -> list[PharmacyMaskModel]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def get_pharmacies(
        self,
        filter_: Optional[FilterPharmacyParamsModel] = None,
    ) -> list[PharmacyModel]:
        raise NotImplementedError
    


class RDBPharmacyRepository(AbstractPharmacyRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def is_pharmacy_existed(self, pharmacy_name: str) -> bool:
        stmt = select(exists(select(Pharmacy).filter(Pharmacy.name == pharmacy_name)))
        return (await self.session.execute(stmt)).scalars().one()
    
    async def get_mask_pharmacy_relation_id(self, pharmacy_id: int,mask_id:int) -> bool:
        stmt = (select(PharmacyMaskPrice.id).filter_by(pharmacy_id =pharmacy_id,mask_id=mask_id))
        return (await self.session.execute(stmt)).scalars().one_or_none()

    def _convert_pharmacy_business_time_schema_to_model(self, pharmacy_business_time: PharmacyBusinessTime) -> PharmacyBusinessTimeModel:
        return PharmacyBusinessTimeModel(
            id=pharmacy_business_time.id,
            business_day=pharmacy_business_time.business_day.name,
            open_time=pharmacy_business_time.open_time,
            close_time=pharmacy_business_time.close_time
        )
    
    def _convert_pharmacy_schema_to_model(self, pharmacy: Pharmacy) -> PharmacyModel:
        return PharmacyModel(
            id=pharmacy.id,
            name=pharmacy.name,
            masks=list(map(self._convert_pharmacy_mask_price_schema_to_model, pharmacy.pharmacy_mask_prices)),
            business_times=list(map(self._convert_pharmacy_business_time_schema_to_model, pharmacy.pharmacy_business_times))
        )
    
    def _convert_pharmacy_mask_price_schema_to_model(self, pharmacy_mask_price: PharmacyMaskPrice) -> PharmacyMaskModel:
        return PharmacyMaskModel(
            id=pharmacy_mask_price.id,
            name=pharmacy_mask_price.mask.name,
            price=pharmacy_mask_price.pharmacy_mask_price,
        )
    
    def _convert_pharmacy_mask_schema_to_model(self, mask: Mask) -> PharmacyMaskModel:
        return PharmacyMaskModel(
            id=mask.id,
            name=mask.name,
            price=mask.pharmacy_mask_prices[0].pharmacy_mask_price,
        )

    async def get_pharmacy_masks(self, pharmacy_name:str,filter_: Optional[FilterPharmacyMaskParamsModel] = None) -> list[PharmacyMaskModel]:
        stmt = select(Mask).join(PharmacyMaskPrice).join(Pharmacy).filter(Pharmacy.name==pharmacy_name)\
            .options(selectinload(Mask.pharmacy_mask_prices).selectinload(PharmacyMaskPrice.pharmacy))

        if filter_:
            offset, limit = filter_.pagination
            stmt = stmt.offset(offset).limit(limit)
        if filter_.order_by:
            if filter_.order_by== PharmacyMaskOrderByEnum.NAME:
                column = getattr(Mask, filter_.order_by)
            else:
                column = getattr(PharmacyMaskPrice,'pharmacy_mask_price')
            column = column.asc() if filter_.ascending else column.desc()
            stmt = stmt.order_by(column)
        
        pharmacy_masks = (await self.session.execute(stmt)).scalars().all()
        return list(map(self._convert_pharmacy_mask_schema_to_model, pharmacy_masks))
    
    async def get_pharmacies(
        self,
        filter_: Optional[FilterPharmacyParamsModel] = None,
    ) -> list[PharmacyModel]:
        stmt = select(Pharmacy).join(PharmacyBusinessTime).join(BusinessDay).join(PharmacyMaskPrice).join(Mask)\
            .options(selectinload(Pharmacy.pharmacy_business_times).selectinload(PharmacyBusinessTime.business_day),
                     selectinload(Pharmacy.pharmacy_mask_prices).selectinload(PharmacyMaskPrice.mask))
        if filter_:
            if filter_.name:
                condition = func.lower(Pharmacy.name).contains(filter_.name.lower(), autoescape=True)
                stmt = stmt.filter(or_(*condition))
            if filter_.order_by:
                column = getattr(Pharmacy, filter_.order_by)
                column = column.asc() if filter_.ascending else column.desc()
                stmt = stmt.order_by(column)

            if filter_.pagination:
                offset, limit = filter_.pagination
                stmt = stmt.offset(offset).limit(limit)

            if filter_.open_time:
                time,day=filter_.open_time
                stmt = stmt.where(BusinessDay.name == day.value)
                if time:
                    stmt = stmt.where(and_(PharmacyBusinessTime.open_time <=time,PharmacyBusinessTime.close_time >= time))
            
            if filter_.mask_price_interval:
                lower_bound,upper_bound = filter_.mask_price_interval
                if lower_bound:
                    stmt = stmt.where(cast(PharmacyMaskPrice.pharmacy_mask_price,DECIMAL) >= lower_bound)
                if upper_bound:
                    stmt = stmt.where(cast(PharmacyMaskPrice.pharmacy_mask_price,DECIMAL) <= upper_bound)
            
            if filter_.mask_type_condition:
                mask_type_count,greater_than = filter_.mask_type_condition
                if mask_type_count:
                    if greater_than:
                        stmt = stmt.group_by(Pharmacy.id).having(func.count(Mask.id)>=mask_type_count)
                    else:
                        stmt = stmt.group_by(Pharmacy.id).having(func.count(Mask.id)<=mask_type_count)
            
        pharmacies = (await self.session.execute(stmt)).scalars().all()

        return list(map(self._convert_pharmacy_schema_to_model, pharmacies))