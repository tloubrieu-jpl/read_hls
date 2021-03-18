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


file_name = '/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.L30.T11SPC.2016007.v1.4.hdf'
output_file = '{}.nc'.format(file_name)
ds = nc.Dataset(output_file, 'w', format='NETCDF4')

file = SD(file_name, SDC.READ)

# print some metadata on the file
print(file.info())
print('---')

attributes_dic = file.attributes()
for idx,att in enumerate(attributes_dic.keys()):
    print(idx,att)
print('---')


# variables value to add in the netcdf
xs = file.attr(10).get() + file.attr(12).get() * np.arange(0,file.attr(8).get()+1, 1.0)
ys = file.attr(11).get() - file.attr(12).get() * np.arange(0,file.attr(9).get()+1, 1.0)
# for later if we want to convert x,y to lat,lon
hdr_dict = get_hdr_dict(file_name + '.hdr')
cs = pycrs.parse.from_ogc_wkt(hdr_dict['coordinate system string'])

fromproj = cs.to_proj4()
toproj = pycrs.parse.from_epsg_code(4326).to_proj4()

transformer = partial(pyproj.transform, fromproj, toproj)

lons, lats = transformer(xs, ys)
ds.createDimension('lat', len(lats))
ds.createDimension('lon', len(lons))
nc_lats = ds.createVariable('lat', 'f4', ('lat',))
nc_lons = ds.createVariable('lon', 'f4', ('lon',))

nc_lats[:] = lats
nc_lons[:] = lons

datasets_dic = file.datasets()
for idx,sds in enumerate(datasets_dic.keys()):
    # add also the values for band01
    current_band = file.select(sds).get()
    ds.createDimension('x_{}'.format(sds), current_band.shape[0])
    ds.createDimension('y_{}'.format(sds), current_band.shape[1])
    nc_current_band = ds.createVariable(sds, 'i4', ('x_{}'.format(sds), 'y_{}'.format(sds),))
    nc_current_band[:] = current_band
