from glob import glob

from convert_hls import ConvertHls

# all_files = glob('/datasets/HLS.S30.T11SPC.20160*.hdf')
#
# for each in all_files:
#     print('converting {}'.format(each))
#     ConvertHls(each).start()

ConvertHls('/Users/wphyo/Projects/HLS/MSLSP/SCC/data/hls/HLS.S30.T11SPC.2016100.v1.4.hdf').start()