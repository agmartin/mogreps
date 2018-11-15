# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Numeric, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class DimDate(Base):
    __tablename__ = 'dim_date'

    id = Column(BigInteger, primary_key=True)
    day = Column(DateTime, nullable=False)
    day_run_label = Column(Text, nullable=False)
    index = Column(BigInteger, nullable=False)


class DimAlt(Base):
    __tablename__ = 'dim_alt'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_alt_id_seq'::regclass)"))
    pressure = Column(Integer, nullable=False)
    altitude = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimAlt.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimAlt.date_valid_start_id == DimDate.id')


class DimLat(Base):
    __tablename__ = 'dim_lat'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_lat_id_seq'::regclass)"))
    latitude = Column(Numeric, nullable=False)
    index = Column(Integer, nullable=False)
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimLat.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimLat.date_valid_start_id == DimDate.id')


class DimLon(Base):
    __tablename__ = 'dim_lon'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_lat_id_seq'::regclass)"))
    longitude = Column(Numeric, nullable=False)
    index = Column(Integer, nullable=False)
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimLon.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimLon.date_valid_start_id == DimDate.id')


class DimMeta(Base):
    __tablename__ = 'dim_meta'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_meta_id_seq'::regclass)"))
    meta_name = Column(Text, nullable=False)
    index = Column(BigInteger, nullable=False)
    latest = Column(Boolean, nullable=False, server_default=text("false"))
    in_process = Column(Boolean, nullable=False, server_default=text("false"))
    files_expected = Column(Integer, nullable=False, server_default=text("696"))
    files_processed = Column(Integer, nullable=False, server_default=text("0"))
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimMeta.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimMeta.date_valid_start_id == DimDate.id')


class DimTime(Base):
    __tablename__ = 'dim_time'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_time_id_seq'::regclass)"))
    offset = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimTime.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimTime.date_valid_start_id == DimDate.id')


class DimModel(Base):
    __tablename__ = 'dim_model'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('dim_model_id_seq'::regclass)"))
    dim_meta_id = Column(ForeignKey('dim_meta.id'), nullable=False)
    index = Column(BigInteger, nullable=False)
    realization = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    date_valid_start_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("1000"))
    date_valid_end_id = Column(ForeignKey('dim_date.id'), nullable=False, server_default=text("999999"))

    date_valid_end = relationship('DimDate', primaryjoin='DimModel.date_valid_end_id == DimDate.id')
    date_valid_start = relationship('DimDate', primaryjoin='DimModel.date_valid_start_id == DimDate.id')
    dim_meta = relationship('DimMeta')


class FactAirTemp1(Base):
    __tablename__ = 'fact_air_temp_1'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('fact_air_temp_1_id_seq'::regclass)"))
    date_id = Column(ForeignKey('dim_date.id'), nullable=False)
    lat_id = Column(ForeignKey('dim_lat.id'), nullable=False)
    lon_id = Column(ForeignKey('dim_lon.id'), nullable=False)
    model_id = Column(ForeignKey('dim_model.id'), nullable=False)
    meta_id = Column(ForeignKey('dim_meta.id'), nullable=False)
    temp_value = Column(Numeric, nullable=False)

    date = relationship('DimDate')
    lat = relationship('DimLat')
    lon = relationship('DimLon')
    meta = relationship('DimMeta')
    model = relationship('DimModel')


class FactVisibilityDist(Base):
    __tablename__ = 'fact_visibility_dist'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('fact_visibility_dist_id_seq'::regclass)"))
    date_id = Column(ForeignKey('dim_date.id'), nullable=False)
    lat_id = Column(ForeignKey('dim_lat.id'), nullable=False)
    lon_id = Column(ForeignKey('dim_lon.id'), nullable=False)
    model_id = Column(ForeignKey('dim_model.id'), nullable=False)
    meta_id = Column(ForeignKey('dim_meta.id'), nullable=False)
    time_id = Column(ForeignKey('dim_time.id'), nullable=False)
    dist_value = Column(Numeric, nullable=False)

    date = relationship('DimDate')
    lat = relationship('DimLat')
    lon = relationship('DimLon')
    meta = relationship('DimMeta')
    model = relationship('DimModel')
    time = relationship('DimTime')


class FactWbulbFreezAlt(Base):
    __tablename__ = 'fact_wbulb_freez_alt'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('fact_wbulb_freez_alt_id_seq'::regclass)"))
    date_id = Column(ForeignKey('dim_date.id'), nullable=False)
    lat_id = Column(ForeignKey('dim_lat.id'), nullable=False)
    lon_id = Column(ForeignKey('dim_lon.id'), nullable=False)
    model_id = Column(ForeignKey('dim_model.id'), nullable=False)
    meta_id = Column(ForeignKey('dim_meta.id'), nullable=False)
    alt_value = Column(Numeric, nullable=False)

    date = relationship('DimDate')
    lat = relationship('DimLat')
    lon = relationship('DimLon')
    meta = relationship('DimMeta')
    model = relationship('DimModel')


class FactXWindSpeed2(Base):
    __tablename__ = 'fact_x_wind_speed_2'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('fact_x_wind_speed_2_id_seq'::regclass)"))
    date_id = Column(ForeignKey('dim_date.id'), nullable=False)
    lat_id = Column(ForeignKey('dim_lat.id'), nullable=False)
    lon_id = Column(ForeignKey('dim_lon.id'), nullable=False)
    alt_id = Column(ForeignKey('dim_alt.id'), nullable=False)
    model_id = Column(ForeignKey('dim_model.id'), nullable=False)
    meta_id = Column(ForeignKey('dim_meta.id'), nullable=False)
    time_id = Column(ForeignKey('dim_time.id'), nullable=False)
    speed_value = Column(Numeric, nullable=False)

    alt = relationship('DimAlt')
    date = relationship('DimDate')
    lat = relationship('DimLat')
    lon = relationship('DimLon')
    meta = relationship('DimMeta')
    model = relationship('DimModel')
    time = relationship('DimTime')
