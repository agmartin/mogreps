import sqlalchemy
import psycopg2
import os
from datetime import datetime
from sqlalchemy import create_engine
from ssm_db_creds import SecureCredsGetter
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from models import *



class DimensionManager():
    
    def __init__(self, file_path):
        self.scg = SecureCredsGetter()
        self.db_dict = self.scg.get_database_dict()
        self.file_path = file_path
        self.engine = create_engine(url.URL(**self.db_dict), echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.meta = {}

    def check_dimension_info(self):
        fn_info = os.path.splitext(os.path.basename(self.file_path).split('-g_')[1])[0]
        date, run, realization, period = fn_info.split('_')

        # get the current date entry and add if not there
        # this is not optimal. In  real life, you would
        # generate a sequence since dates are known in advance

        current_date = self.session.query(DimDate)\
            .filter(DimDate.index==date+run).first()
        if current_date:
            cd_id = current_date.id
        else:
            last_id = current_date = self.session.query(func.max(DimDate.id))\
                .filter(DimDate.id < 999999).first()[0]

            dt = datetime.strptime(date+run,'%Y%m%d%H')
            d = DimDate(id=last_id+1,
                        day=dt,
                        day_run_label = date + ' ' + run + ' ' + 'Zulu',
                        index=date+run)
            self.session.add(d)
            self.session.commit()

            newest_date = self.session.query(DimDate)\
                .filter(DimDate.index==date+run).first()
            cd_id = newest_date.id

        # add this to the dict we need to return for the FactManager
        # to use
        self.meta['date_id'] = cd_id

        # check to see if this file has been processed before
        # if not, add to meta
        current_meta = self.session.query(DimMeta)\
            .filter(DimMeta.index==date+run).first()

        if current_meta:
            cm_id = current_meta.id
        else:
            m = DimMeta(meta_name='mogreps-g',
                        index=date+run)
            self.session.add(m)
            self.session.commit()

            newest_meta = self.session.query(DimMeta)\
                .filter(DimMeta.index==date+run).first()

            cm_id = newest_meta.id

        self.meta['meta_id'] = cm_id

        # finally, check to see if the model run info exists and do the same.

        current_model = self.session.query(DimModel)\
            .filter(DimModel.dim_meta_id==self.meta['meta_id'])\
            .filter(DimModel.index==realization.strip('0')+period.strip('0')).first()

        if current_model:
            cmod_id = current_model.id
        else:
            mod = DimModel(dim_meta_id=self.meta['meta_id'],
                        index=realization.strip('0')+period.strip('0'),
                        realization=realization,
                        period=period)
            self.session.add(mod)
            self.session.commit()

            newest_model = self.session.query(DimModel)\
            .filter(DimModel.dim_meta_id==self.meta['meta_id'])\
            .filter(DimModel.index==realization.strip('0')+period.strip('0')).first()

            cmod_id = newest_model.id

        self.meta['model_id'] = cmod_id


    def get_dim_ids(self):
        lats = self.session.query(DimLat).all()
        lats_ids = {float(item.index):item.id for item in lats}
        self.meta['lat'] = lats_ids

        lons = self.session.query(DimLon).all()
        lons_ids = {float(item.index):item.id for item in lons}
        self.meta['lon'] = lons_ids

        alts = self.session.query(DimAlt).all()
        alts_ids = {item.index:item.id for item in alts}
        self.meta['alt'] = alts_ids

        times = self.session.query(DimTime).all()
        times_ids = {item.index:item.id for item in times}
        self.meta['time'] = times_ids

        return self.meta









