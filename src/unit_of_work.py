from settings import IS_TEST
from settings.database import AsyncScopedSession
from repositories.pharmacy import RDBPharmacyRepository
from repositories.user import RDBUserRepository
from repositories.purchase_record import RDBPurchaseRecordRepository
from repositories.mask import RDBMaskRepository


class AsyncSqlAlchemyUnitOfWork:
    _pharmacy_repo = RDBPharmacyRepository
    _user_repo=RDBUserRepository
    _purchase_record_repo=RDBPurchaseRecordRepository
    _mask_repo=RDBMaskRepository

    def __init__(self):
        session = AsyncScopedSession()
        self._session = session
        self.pharmacy_repo = self._pharmacy_repo(session)
        self.user_repo=self._user_repo(session)
        self.purchase_record_repo=self._purchase_record_repo(session)
        self.mask_repo=self._mask_repo(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        await self._session.close()

        # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.async_scoped_session.remove
        if not IS_TEST:
            await AsyncScopedSession.remove()
