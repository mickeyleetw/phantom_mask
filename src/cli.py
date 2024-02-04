# pylint: disable=import-outside-toplevel

import asyncio
import functools
from typing import Optional
from pathlib import Path

import typer
import uvicorn
from sqlalchemy import MetaData, schema
from data_importer import JSON_DATA_LIST ,CSV_DATA_LIST
from data_importer.data_importer import json_file_processor,csv_processor


app = typer.Typer()
app_path = Path(__file__).resolve().parent.name

def coroutine(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@app.command()
def run(reload: Optional[bool] = False):
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8003,
        app_dir='src',
        reload=reload,
        http='h11'
    )



@app.command()
def reset_db():
    purge_db()
    create_schema()
    create_tables()
    import_data()


@app.command()
@coroutine
async def purge_db():
    from settings.database import DB_SCHEMA, async_engine, get_schema_names

    async with async_engine.begin() as connection:
        existed_schemas = await connection.run_sync(get_schema_names)
        meta_data = MetaData(bind=async_engine)
        if DB_SCHEMA in existed_schemas:
            await connection.run_sync(meta_data.reflect, schema=DB_SCHEMA)
            print('Dropping db schema...')
            await connection.run_sync(meta_data.drop_all)
        await async_engine.dispose()
        print('purge db successful.')


@app.command()
@coroutine
async def create_schema():
    from settings.database import DB_SCHEMA, async_engine, get_schema_names

    async with async_engine.begin() as connection:
        existed_schemas = await connection.run_sync(get_schema_names)
        # pylint: disable=no-member
        if async_engine.dialect.name == 'postgresql' and DB_SCHEMA not in existed_schemas:
            print('Creating db schema...')
            await connection.execute(schema.CreateSchema(DB_SCHEMA))
            print('create db schema successful.')
        await async_engine.dispose()


@app.command()
@coroutine
async def create_tables():
    import schemas  # noqa (autoflake)
    from settings.database import Base, async_engine

    async with async_engine.begin() as connection:
        print('Creating db Tables...')
        for k in Base.metadata.tables.keys():  # pylint: disable=no-member
            print(f'  - {k}')

        # pylint: disable=no-member
        await connection.run_sync(Base.metadata.create_all)
        await async_engine.dispose()
        print('Create tables successful.')

@app.command()
@coroutine
async def import_data():
    from settings.database import async_engine
    async with async_engine.begin() as connection:
        print('Start import csv file')
        await csv_processor(db_connection=connection,app_path=app_path, data_list=CSV_DATA_LIST)
        await async_engine.dispose()
        print('csv data imported successfully.')
    print('Start import json file')
    await json_file_processor(app_path=app_path, data_list=JSON_DATA_LIST)
    print('json data imported successfully.')



if __name__ == '__main__':
    app()
