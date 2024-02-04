import abc
from typing import Optional
from sqlalchemy import func

from sqlalchemy.sql.expression import select,or_


from schemas.pharmacy import Mask
from models.mask import FilterMaskParamsModel,MaskModel
from settings.database import AsyncSession

class AbstractMaskRepository(abc.ABC):
    
    @abc.abstractmethod
    async def get_masks(
        self,
        filter_: Optional[FilterMaskParamsModel] = None,
    ) -> list[MaskModel]:
        raise NotImplementedError

class RDBMaskRepository(AbstractMaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @staticmethod
    def _convert_mask_schema_to_model(mask: Mask) -> MaskModel:
        return MaskModel(
            id=mask.id,
            name=mask.name
        )
    
    
    async def get_masks(
        self,
        filter_: Optional[FilterMaskParamsModel] = None,
    ) -> list[MaskModel]:
        
        stmt = select(Mask)
        if filter_:
            if filter_.name:
                condition = func.lower(Mask.name).contains(filter_.name.lower(), autoescape=True)
                stmt = stmt.filter(or_(*condition))
            if filter_.order_by:
                column = getattr(Mask, filter_.order_by.value)
                column = column.asc() if filter_.ascending else column.desc()
                stmt = stmt.order_by(column)
        
        masks=(await self.session.execute(stmt)).scalars().all()
        return list(map(self._convert_mask_schema_to_model, masks))