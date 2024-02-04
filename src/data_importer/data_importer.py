import csv
import os
import json
from sqlalchemy import text
from decimal import Decimal
from sqlalchemy.sql.expression import exists, select
from settings import ENV
from schemas.pharmacy import Pharmacy, Mask, PharmacyMaskPrice
from schemas.business_time import PharmacyBusinessTime
from schemas.user import User, UserPurchaseHistory
from settings.database import AsyncScopedSession, DB_SCHEMA
import re
from datetime import datetime

async def csv_processor(db_connection,app_path: str, data_list: list):
    table_list = list(dict())
    for path in data_list:
        file_path = f'{app_path}/{path}' if ENV == 'local' else f'/{app_path}/{path}'
        _, file_name = os.path.split(file_path)
        table_name = file_name.split('.csv')[0]
        with open(file_path, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
            table_list.append({'name': table_name, 'cols': data[0], 'data': data[1:]})
        
        for table_set in table_list:
            table_name = table_set.get('name')
            table_cols = table_set.get('cols')
            raw_datas = table_set.get('data')
            raw_sql = f'INSERT INTO {DB_SCHEMA}.{table_name}({{cols}}) VALUES({{vals}});'
            cols = ','.join(table_cols)
            for data_raw in raw_datas:
                import_data = '\'{0}\''.format('\', \''.join(data_raw))
                sql = raw_sql.format(cols=cols, vals=import_data)
                await db_connection.execute(text(sql))

async def json_file_processor(app_path: str, data_list: list):
    async with AsyncScopedSession() as session:
        for path in data_list:
            file_path = f'{app_path}/{path}' if ENV == 'local' else f'/{app_path}/{path}'
            _, file_name = os.path.split(file_path)

            # insert pharmacy.json
            if file_name.split('.json')[0] == 'pharmacies':
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    for data in json_data:
                        
                        # insert pharmacy mask price relationship
                        pharmacy_mask_price_list=[]
                        masks=data['masks']
                        for mask_data in masks:
                            if ((await session.execute(select(exists(select(Mask).filter(Mask.name == mask_data['name']))))).scalars().one()):
                                mask= (await session.execute((select(Mask).filter(Mask.name == mask_data['name'])))).scalars().one()
                                pharmacy_mask_price_list.append(PharmacyMaskPrice(mask_id=mask.id,pharmacy_mask_price=Decimal(mask_data['price'])))
                            else:
                                pharmacy_mask_price_list.append(PharmacyMaskPrice(mask=Mask(name=mask_data['name']),pharmacy_mask_price=Decimal(mask_data['price'])))
                        
                        # insert pharmacy business time relationship
                        pharmacy_open_time_list=[]
                        open_times=data['openingHours']
                        business_day_id_map={'Mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6,'Sun':7}
                        open_time_list=open_times.split(' / ')
                        for open_time in open_time_list:
                            open_time=open_time.replace("Thur","Thu")
                            if open_time.count('-')==1:
                                pattern = r"(\w{3})(?:,\s(\w{3}))?(?:,\s(\w{3}))?\s(\d{2}:\d{2})\s-\s(\d{2}:\d{2})"
                                matches = re.findall(pattern, open_time)[0]
                                open_time= datetime.strptime(matches[-2], '%H:%M').time()
                                close_time=datetime.strptime(matches[-1], '%H:%M').time()
                                days=matches[:-2]
                                for day in days:
                                    if day=='':
                                        continue
                                    pharmacy_open_time_list.append(PharmacyBusinessTime(business_day_id=business_day_id_map[day],open_time=open_time,close_time=close_time))
                            elif open_time.count('-')==2:
                                regex_2 = r"(\w{3})(?: - (\w{3}))? (\d{2}:\d{2}) - (\d{2}:\d{2})"
                                matches = re.findall(regex_2, open_time)[0]
                                open_time= datetime.strptime(matches[-2], '%H:%M').time()
                                close_time=datetime.strptime(matches[-1], '%H:%M').time()
                                for i in list(range(business_day_id_map[matches[0]],business_day_id_map[matches[1]]+1,1)):
                                    pharmacy_open_time_list.append(PharmacyBusinessTime(business_day_id=i,open_time=open_time,close_time=close_time))
                            
                        # insert pharmacy data
                        new_store = Pharmacy(
                            name=data['name'],
                            cash_balance=Decimal(data['cashBalance']),
                            pharmacy_mask_prices=pharmacy_mask_price_list,
                            pharmacy_business_times=pharmacy_open_time_list
                        )
                        session.add(new_store)
                        await session.flush()
            elif file_name.split('.json')[0] == 'users':
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    for data in json_data:
                        # insert user purchase history relationship
                        purchase_histories=data['purchaseHistories']
                        purchase_history_list=[]
                        for purchase_history in purchase_histories:
                            mask_id=(await session.execute((select(Mask.id).filter(Mask.name == purchase_history['maskName'])))).scalars().one()
                            pharmacy_id=(await session.execute((select(Pharmacy.id).filter(Pharmacy.name == purchase_history['pharmacyName'])))).scalars().one()
                            pharmacy_mask_id= (await session.execute((select(PharmacyMaskPrice.id)\
                                .filter_by(mask_id=mask_id,pharmacy_id=pharmacy_id)))).scalars().one()
                            purchase_history_list.append(UserPurchaseHistory(pharmacy_mask_price_id=pharmacy_mask_id,transaction_amount=Decimal(purchase_history['transactionAmount']),transaction_date=datetime.strptime(purchase_history['transactionDate'], '%Y-%m-%d %H:%M:%S')))
                                                # insert pharmacy data
                        new_user = User(
                            name=data['name'],
                            cash_balance=Decimal(data['cashBalance']),
                            user_purchase_histories=purchase_history_list
                        )
                        session.add(new_user)
                        await session.flush()
            session.expunge_all()
        await session.commit()