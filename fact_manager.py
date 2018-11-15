import netCDF4
import sqlalchemy
import psycopg2
import os
import io
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
from ssm_db_creds import SecureCredsGetter
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func
from sqlalchemy.engine import reflection
from sqlalchemy import MetaData, Table, ForeignKeyConstraint
from sqlalchemy.schema import DropConstraint, AddConstraint
from utils import drop_foreign_keys, restore_foreign_keys


from models import *


class FactManager():
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.scg = SecureCredsGetter()
        self.db_dict = self.scg.get_database_dict()
        self.engine = create_engine(url.URL(**self.db_dict), echo=False)

    def manage_fact_wbulb_freez_alt(self, ids):

        table_name = 'fact_wbulb_freez_alt'
        data = netCDF4.Dataset(self.file_path)
        wb_data = data.variables['wet_bulb_freezing_level_altitude']

        fact_list = []

        for x, lat_dim in enumerate(wb_data):
            for i, val in enumerate(lat_dim):
                date_id = ids['date_id']
                lat_id = ids['lat'][x]
                lon_id = ids['lon'][i]
                model_id = ids['model_id']
                meta_id = ids['meta_id']
                alt_value = float(val)

                fact_tmp = [date_id, lat_id, lon_id, model_id, meta_id, alt_value]
                fact_list.append(fact_tmp)

        fact_columns = ['date_id', 'lat_id', 'lon_id', 'model_id', 'meta_id', 'alt_value']
        df = pd.DataFrame(fact_list, columns=fact_columns)

        fact_csv = io.StringIO()
        df.to_csv(fact_csv, index=False, header=False)
        fact_csv.seek(0)

        #  this locks the database
        # print('dropping foreign keys')
        # drop_foreign_keys(table_name, self.engine)
        # print('finished dropping foreign keys')

        conn = self.engine.raw_connection()
        cur = conn.cursor()

        print('starting database copy action', datetime.now())
        cur.copy_from(fact_csv, table_name, sep=",", columns=fact_columns)
        conn.commit()
        cur.close()
        conn.close()
        print('db copy complete', datetime.now())

        # print('restoring foreign keys')
        # restore_foreign_keys(table_name, self.engine)
        # print('finished restoring keys')


    def check_lat_dim(self, cube, ids):
        dims = [coord.name() for coord in cube.dim_coords]
        ix = dims.index('latitude')
        lats = [float(val.cell(0)[0]) for val in cube.dim_coords[ix]]

        for i, lat in enumerate(lats):
            try:
                ids['lat'][lat]
            except KeyError:
                lat_entry = DimLat(
                    latitude=lat,
                    index=i
                    )
                self.session.add(lat_entry)
                self.session.commit()
                pass


    def check_lon_dim(self, cube, ids):
        dims = [coord.name() for coord in cube.dim_coords]
        ix = dims.index('longitude')
        lons = [float(val.cell(0)[0]) for val in cube.dim_coords[ix]]

        for i, lon in enumerate(lons):
            try:
                ids['lon'][lon]
            except KeyError:
                lon_entry = DimLon(
                    longitude=lon,
                    index=i
                    )
                self.session.add(lon_entry)
                self.session.commit()
                pass


    def remove_foreign_keys(self, engine):

        inspector = reflection.Inspector.from_engine(engine)

        fake_metadata = MetaData()

        table = 'fact_wbulb_freez_alt'
        fake_tables = []
        all_fks = []

        for table_name in Base.metadata.tables:
            if table_name == table:
                fks = []
                for fk in inspector.get_foreign_keys(table_name):
                    if fk['name']:
                        fks.append(ForeignKeyConstraint((),(),name=fk['name']))
                t = Table(table_name, fake_metadata, *fks)
                fake_tables.append(t)
                all_fks.extend(fks)

        connection = engine.connect()
        transaction = connection.begin()
        for fkc in all_fks:
            print(fkc)
            connection.execute(DropConstraint(fkc))
        transaction.commit()



