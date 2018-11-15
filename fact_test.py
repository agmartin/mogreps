import netCDF4
import sqlalchemy
import psycopg2
import os
import csv
import io
# import iris
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func
import numpy as np
import pandas as pd


from models import *

try:
    from secure_db_creds import DATABASE as creds
except:
    from db_creds import DATABASE as creds

# file_path = file_path
engine = create_engine(url.URL(**creds), echo=False)
Session = sessionmaker(bind=engine)
session = Session()
meta = {}
# cubes = iris.load(file_path)
DBSession = scoped_session(sessionmaker())
DBSession.remove()
DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)

data = netCDF4.Dataset('./raw_data/mogreps-test.nc')

wb_data = data.variables['wet_bulb_freezing_level_altitude']

obj_list = []

print('starting tight loop', datetime.now())
for i, lat_dim in enumerate(wb_data):
    for j, val in enumerate(lat_dim):
        date_id = ids['date_id']
        lat_id = ids['lat'][x]
        lon_id = ids['lon'][i]
        model_id = ids['model_id']
        meta_id = ids['meta_id']
        value = float(dim1)

        fact = [1001, 4915, 5515, 1002, 1001, float(val)]
        obj_list.append(fact)
print('finished tight loop', datetime.now())

df = pd.DataFrame(np.array(obj_list), columns = ['date_id', 'lat_id', 'lon_id', 'model_id', 'meta_id', 'value'])



# print('bulk insert start', datetime.now())
# df.to_sql(name='fact_wbulb_freez_alt', con=engine, if_exists = 'append', index=False)


# DBSession.bulk_save_objects(obj_list[0:10000])
# DBSession.commit()
# print('bulk insert finished', datetime.now())

df.to_csv('test.csv', index=False)
