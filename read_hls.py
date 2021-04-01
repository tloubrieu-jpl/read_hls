from datetime import datetime

from pyhdf.SD import SD, SDC
import pycrs
import pyproj
from functools import partial
import numpy as np

import netCDF4 as nc


def get_hdr_dict(filename):
    hdr_dict = {}
    with open(filename, 'r') as f_hdr:
        for line in f_hdr.readlines():
            first_equal = line.find('=')
            if first_equal>=0:
                hdr_dict[line[:first_equal-1].strip(' \n')] = line[first_equal+1:].strip(' \n')
    return hdr_dict


file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016100.v1.4.hdf'
# file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016107.v1.4.hdf'
# file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016110.v1.4.hdf'
# file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016020.v1.4.hdf'
# file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016117.v1.4.hdf'
# file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.L30.T11SPC.2016023.v1.4.hdf'


"""
            start_time = datetime.datetime.strptime(self.__output_name[1:7], '%y%m%d')
        elif aviris_ng.match(self.__output_name):
            start_time = datetime.datetime.strptime(self.__output_name[3:18], '%Y%m%dt%H%M%S')
        else:
            raise RuntimeError('not implemented for dataset name: {}'.format(self.__output_name))
        return start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
"""

output_file = '{}.nc'.format(file_name)
ds = nc.Dataset(output_file, 'w', format='NETCDF4')

file = SD(file_name, SDC.READ)

# print some metadata on the file
print(file.info())
print('---')

attributes_dic = file.attributes()
utm_keys = ['ULX', 'ULY', 'NROWS', 'NCOLS', 'SPATIAL_RESOLUTION']

if all(k in attributes_dic for k in utm_keys) is False:
    raise RuntimeError('missing one or more keys in file attributes. keys: {}'.format(utm_keys))

# variables value to add in the netcdf
"""
0 SENSOR
1 LANDSAT_SCENE_ID
2 LANDSAT_PRODUCT_ID
3 DATA_TYPE
4 SENSING_TIME
5 L1_PROCESSING_TIME
6 USGS_SOFTWARE
7 HORIZONTAL_CS_NAME
8 NROWS
9 NCOLS
10 ULX
11 ULY
12 SPATIAL_RESOLUTION
13 MEAN_SUN_ZENITH_ANGLE
14 MEAN_SUN_AZIMUTH_ANGLE
15 TIRS_SSM_MODEL
16 TIRS_SSM_POSITION_STATUS
17 ACCODE
18 SENTINEL2_TILEID
19 arop_s2_refimg
20 arop_ncp
21 arop_rmse(meters)
22 arop_ave_xshift(meters)
23 arop_ave_yshift(meters)
24 NBAR_Solar_Zenith
25 HLS_PROCESSING_TIME
26 spatial_coverage
27 cloud_coverage
28 StructMetadata.0
"""
xs = attributes_dic['ULX'] + int(attributes_dic['SPATIAL_RESOLUTION']) * np.arange(0, int(attributes_dic['NROWS']), 1.0)
ys = attributes_dic['ULY'] - int(attributes_dic['SPATIAL_RESOLUTION']) * np.arange(0, int(attributes_dic['NCOLS']), 1.0)
# for later if we want to convert x,y to lat,lon
hdr_dict = get_hdr_dict(file_name + '.hdr')
cs = pycrs.parse.from_ogc_wkt(hdr_dict['coordinate system string'])

fromproj = cs.to_proj4()
toproj = pycrs.parse.from_epsg_code(4326).to_proj4()

transformer = partial(pyproj.transform, fromproj, toproj)

lons, lats = transformer(xs, ys)


ds.createDimension('utm_x', len(xs))
ds.createDimension('utm_y', len(ys))
ds.createDimension('static_time', 1)
nc_lons = ds.createVariable('utm_x', 'f4', ('utm_x',), zlib=True)
nc_lats = ds.createVariable('utm_y', 'f4', ('utm_y',), zlib=True)

file_datetime = datetime.strptime('{}+0000'.format(file_name.split('.')[3]), '%Y%j%z')
dt_since = datetime.strptime('1981001+0000', '%Y%j%z')
filling_dt = int(file_datetime.timestamp()) - int(dt_since.timestamp())

nc_time = ds.createVariable('static_time', 'i4', ('static_time',), zlib=True)
nc_time[:] = np.full((1, ), filling_dt)
nc_time.long_name = 'reference time of sst field'
nc_time.standard_name = 'time'
nc_time.axis = 'T'
nc_time.units = 'seconds since 1981-01-01 00:00:00 UTC'
nc_time.comment = 'Nominal time of analyzed fields'

nc_lats[:] = lats
nc_lons[:] = lons
# nc_lats[:] = ys
# nc_lons[:] = xs
datasets_dic = file.datasets()
for idx,sds in enumerate(datasets_dic.keys()):
    # add also the values for band01
    current_band = file.select(sds).get()

    nc_current_band = ds.createVariable(sds, 'i4', ('utm_x', 'utm_y',), zlib=True)
    nc_current_band[:] = current_band
