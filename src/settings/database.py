import os
from asyncio import current_task
from datetime import datetime
from typing import AsyncIterable

import sqlalchemy.orm
from sqlalchemy import Column, DateTime, Integer, MetaData, inspect
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session, create_async_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.future.engine import Connection
from sqlalchemy.orm import backref as _backref
from sqlalchemy.orm import relationship as _relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.session import Session

from settings import APP, IS_DEBUG


DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '5440'))
DB_USERNAME = os.getenv('DB_USER', APP)
DB_PASSWORD = os.getenv('DB_PASSWORD') or APP
DB_NAME = os.getenv('DB_NAME', APP)
DB_SCHEMA = os.getenv('DB_SCHEMA', APP)

db_url = URL.create(
    'postgresql+asyncpg',
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)
async_engine = create_async_engine(
    db_url,
    # pool_size=DB_MAXCONN,
    # max_overflow=DB_OVERFLOW,
    isolation_level='REPEATABLE READ',
    echo=IS_DEBUG,
    connect_args={
        'server_settings': {
            'application_name': 'phantom-mask'  # TODO: check the usage
        }
    }
)
sqlalchemy.orm.relationship = lambda *args, **kwargs: _relationship(lazy=kwargs.pop('lazy', 'raise'), *args, **kwargs)
sqlalchemy.orm.backref = lambda *args, **kwargs: _backref(lazy=kwargs.pop('lazy', 'raise'), *args, **kwargs)


@as_declarative(metadata=MetaData(schema=DB_SCHEMA))
class Base:
    __abstract__ = True

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, default=datetime.utcnow, index=True)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)


class AsyncSession(_AsyncSession):  # pylint: disable=abstract-method

    def __init__(self, *args, **kargs):
        super().__init__(sync_session_class=Session, *args, **kargs)

    async def set_flag_modified(self, instance, key: str):
        # https://docs.sqlalchemy.org/en/14/core/defaults.html
        # https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.attributes.flag_modified
        flag_modified(instance, key)


AsyncScopedSession = async_scoped_session(
    sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    ),
    scopefunc=current_task 
)


async def get_session() -> AsyncIterable[AsyncSession]:
    async with AsyncScopedSession() as session:
        yield session


def get_schema_names(conn: Connection) -> list[str]:
    inspector = inspect(conn)
    return inspector.get_schema_names()
