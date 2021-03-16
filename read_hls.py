from pyhdf.SD import SD, SDC
import pycrs
import pyproj
from functools import partial
import numpy as np


def get_hdr_dict(filename):
    hdr_dict = {}
    with open(filename, 'r') as f_hdr:
        for line in f_hdr.readlines():
            first_equal = line.find('=')
            if first_equal>=0:
                hdr_dict[line[:first_equal-1].strip(' \n')] = line[first_equal+1:].strip(' \n')
    return hdr_dict


file_name = '/Users/loubrieu/Documents/sdap/HLS/HLS.L30.T01UFU.2021003.v1.4.hdf'

file = SD(file_name, SDC.READ)

# print some metadata on the file
print(file.info())

datasets_dic = file.datasets()
for idx,sds in enumerate(datasets_dic.keys()):
    print(idx,sds)


attributes_dic = file.attributes()
for idx,att in enumerate(attributes_dic.keys()):
    print(idx,att)


# variables value to add in the netcdf
xs = file.attr(10).get() + file.attr(12).get() * np.arange(0,file.attr(8).get()+1, 1.0)
ys = file.attr(11).get() - file.attr(12).get() * np.arange(0,file.attr(9).get()+1, 1.0)

# add also the values for band01
band01 = file.select('band01').get()

# and other datasets
# ...

# for later if we want to convert x,y to lat,lon
hdr = file_name + '.hdr'
hdr_dict = get_hdr_dict(hdr)
cs = pycrs.parse.from_ogc_wkt(hdr_dict['coordinate system string'])


fromproj = cs.to_proj4()
toproj = pycrs.parse.from_epsg_code(4326).to_proj4()

transformer = partial(pyproj.transform, fromproj, toproj)

lons, lats = transformer(xs, ys)

## try to see if converted coordinates are regular
lon2000, lat2000 = transformer(xs[2000], ys[2000])
print(lons[2000], lon2000)
print(lats[2000], lat2000)





