from glob import glob

from convert_hls import ConvertHls
with open('/tmp/glob.txt', 'r') as f:
    glob_expr = f.read()
all_files = glob(glob_expr.strip())

for each in all_files:
    print('converting {}'.format(each))
    ConvertHls(each).start()
