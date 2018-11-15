# coding=utf-8
"""
Ingest data from the command-line.
Mogreps data from the UK Met Office
"""
from __future__ import absolute_import

import uuid
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from pathlib import Path
import xarray as xr

import click
import netCDF4
import yaml


def find_interesting_vars(nco):
    interesting_variables = {vname: v
                             for vname, v in nco.variables.items()
                             if 'grid_mapping' in v.ncattrs()}
    groups = {}
    data = interesting_variables.values()
    get_dimensions = attrgetter('dimensions')
    data = sorted(data, key=get_dimensions)
    for k, g in groupby(data, get_dimensions):
        groups[k] = list(g)  # Store group iterator as a list

    return groups


def generate_product(variables):
    prod_name = '_'.join(v.name for v in variables)
    return {
        'name': prod_name,
        'description': prod_name,
        'metadata_type': 'eo',
        'metadata': {
            'platform': {'code': 'mogreps'},
            'product_type': prod_name,
            'format': {
                'name': 'NETCDF'
            }
        },
        'measurements': [
            {'name': v.name,
             'dtype': str(v.dtype),
             'units': str(v.units),
             'nodata': float(v._FillValue)}
            for v in variables
        ]
    }


def find_bounds(filename, dims):
    bounds = {}
    with xr.open_dataset(filename) as ds:
        for dim in dims:
            coord = ds[dim]
            if 'axis' not in coord.attrs:
                continue
            if coord.axis == 'X':
                bounds['left'] = float(coord.min())
                bounds['right'] = float(coord.max())
            elif coord.axis == 'Y':
                bounds['top'] = float(coord.max())
                bounds['bottom'] = float(coord.min())
            elif coord.axis == 'T':
                bounds['start'] = coord.min().data
                bounds['end'] = coord.max().data
    return bounds


def make_dataset(filename, dims, variables):
    bounds = find_bounds(filename, dims)

    p = Path(filename)

    mtime = datetime.fromtimestamp(p.stat().st_mtime)
    return {
        'id': str(uuid.uuid4()),
        'processing_level': 'modelled',
        'product_type': 'gamma_ray',
        'creation_dt': mtime.isoformat(),
        'extent': {
            'coord': {
                'ul': {'lon': bounds['left'], 'lat': bounds['top']},
                'ur': {'lon': bounds['right'], 'lat': bounds['top']},
                'll': {'lon': bounds['left'], 'lat': bounds['bottom']},
                'lr': {'lon': bounds['right'], 'lat': bounds['bottom']},
            },
            'from_dt': str(bounds['start']),
            'to_dt': str(bounds['end']),
        },
        'format': {'name': 'NetCDF'},
        'image': {
            'bands': {
                variable.name: {
                    'path': filename,
                    'layername': variable.name,
                } for variable in variables
            }
        },
        'lineage': {'source_datasets': {}},
    }


# @click.group()
# def cli():
#     pass


# @cli.command(help="Create product definitions from mogreps NetCDF File")
# @click.argument('filename', type=click.Path(exists=True, readable=True))
def products(filename):
    prods = []
    with netCDF4.Dataset(filename) as nco:
        groups = find_interesting_vars(nco)
        for dims, grouped_vars in groups.items():
            prods.append(generate_product(grouped_vars))
    print(yaml.safe_dump_all(prods))


# @cli.command(help="Create dataset definitions from a mogreps NetCDF File")
# @click.argument('filename', type=click.Path(exists=True, readable=True))
def datasets(filename):
    datasets = []
    with netCDF4.Dataset(filename) as nco:
        groups = find_interesting_vars(nco)
        return groups
    #     for dims, grouped_vars in groups.items():
    #         try:
    #             ds = make_dataset(filename, dims, grouped_vars)
    #             datasets.append(ds)
    #         except Exception as e:
    #             print(e)
    # print(yaml.safe_dump_all(datasets))


# if __name__ == "__main__":
#     cli()
