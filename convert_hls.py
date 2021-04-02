import os
from datetime import datetime

from pyhdf.SD import SD, SDC
import pycrs
import pyproj
from functools import partial
import numpy as np

import netCDF4 as nc


class ConvertHls:
    def __init__(self, input_file):
        if not os.path.exists(input_file) or not os.path.isfile(input_file):
            raise ValueError('input file missing')
        self.__input_file = input_file
        self.__sd_file = None
        self.__ds_output = None
        pass

    def __get_hdr_dict(self, filename):
        hdr_dict = {}
        with open(filename, 'r') as f_hdr:
            for line in f_hdr.readlines():
                first_equal = line.find('=')
                if first_equal >= 0:
                    hdr_dict[line[:first_equal - 1].strip(' \n')] = line[first_equal + 1:].strip(' \n')
        return hdr_dict

    def __convert_to_lat_lon(self):
        attributes_dic = self.__sd_file.attributes()
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
        xs = attributes_dic['ULX'] + int(attributes_dic['SPATIAL_RESOLUTION']) * np.arange(0,
                                                                                           int(attributes_dic['NROWS']),
                                                                                           1.0)
        ys = attributes_dic['ULY'] - int(attributes_dic['SPATIAL_RESOLUTION']) * np.arange(0,
                                                                                           int(attributes_dic['NCOLS']),
                                                                                           1.0)
        # for later if we want to convert x,y to lat,lon
        hdr_dict = self.__get_hdr_dict('{}.hdr'.format(self.__input_file))
        cs = pycrs.parse.from_ogc_wkt(hdr_dict['coordinate system string'])

        fromproj = cs.to_proj4()
        toproj = pycrs.parse.from_epsg_code(4326).to_proj4()

        transformer = partial(pyproj.transform, fromproj, toproj)
        lons, lats = transformer(xs, ys)

        self.__ds_output.createDimension('utm_x', len(lons))
        self.__ds_output.createDimension('utm_y', len(lats))
        nc_lons = self.__ds_output.createVariable('utm_x', 'f4', ('utm_x',), zlib=True)
        nc_lats = self.__ds_output.createVariable('utm_y', 'f4', ('utm_y',), zlib=True)
        nc_lats[:] = lats
        nc_lons[:] = lons
        # nc_lats[:] = ys
        # nc_lons[:] = xs
        return

    def __capture_time(self):
        file_datetime = datetime.strptime('{}+0000'.format(self.__input_file.split('.')[3]), '%Y%j%z')
        dt_since = datetime.strptime('1981001+0000', '%Y%j%z')
        filling_dt = int(file_datetime.timestamp()) - int(dt_since.timestamp())

        self.__ds_output.createDimension('static_time', 1)
        nc_time = self.__ds_output.createVariable('static_time', 'i4', ('static_time',), zlib=True)

        nc_time[:] = np.full((1,), filling_dt)
        nc_time.long_name = 'reference time of sst field'
        nc_time.standard_name = 'time'
        nc_time.axis = 'T'
        nc_time.units = 'seconds since 1981-01-01 00:00:00 UTC'
        nc_time.comment = 'Nominal time of analyzed fields'
        return

    def __capture_bands(self):
        datasets_dic = self.__sd_file.datasets()
        for idx, sds in enumerate(datasets_dic.keys()):
            attributes_dic = self.__sd_file.select(sds).attributes()
            # add also the values for band01
            current_band = self.__sd_file.select(sds).get()
            nc_current_band = self.__ds_output.createVariable(sds, 'i4', ('utm_x', 'utm_y',), zlib=True)
            nc_current_band[:] = current_band
            for k, v in attributes_dic.items():
                if k != '_FillValue':
                    nc_current_band.setncattr(k, v)
        return

    def start(self):
        self.__ds_output = nc.Dataset('{}.nc'.format(self.__input_file), 'w', format='NETCDF4')
        self.__sd_file = SD(self.__input_file, SDC.READ)
        self.__convert_to_lat_lon()
        self.__capture_time()
        self.__capture_bands()
        return
    pass
