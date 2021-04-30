import os
import sys
import logging
from pathlib import Path
import argparse
import requests
from bs4 import BeautifulSoup
from convert_hls import ConvertHls

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DATA_URL = 'https://hls.gsfc.nasa.gov/data/v1.4'




def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent


def download_file_url(url, output_dir):
    response = requests.get(url)
    filename = url.split('/')[-1]
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    open(file_path, 'wb').write(response.content)
    return file_path


def main():
    parser = argparse.ArgumentParser(description='Process tiles')
    parser.add_argument('--type', type=str, default='S30',
                        help='L30 or S30, default S30')
    parser.add_argument('--years', type=int,
                        help='year to be downloaded and converted')
    parser.add_argument('--tiles', type=str,
                        help='tile code to be processed, for example 18TYN')
    parser.add_argument('--tmp-dir', type=str, default='/tmp',
                        help='tmp dir where files are downloaded before conversion')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='default output dir where converted files are pushed')

    args = parser.parse_args()

    tile = args.tiles
    year = args.years

    year_tile_url = f'{DATA_URL}/{args.type}/{year}/{tile[:2]}/{tile[2]}/{tile[3]}/{tile[4]}/'

    logger.info("Reading files in %s", year_tile_url)

    hdf_files = get_url_paths(year_tile_url, 'hdf')

    for hdf_file in hdf_files:

        hdf_local = download_file_url(hdf_file, args.tmp_dir)
        logger.info("Save local file %s", hdf_local)

        hdr_file = f'{hdf_file}.hdr'
        hdr_local = download_file_url(hdr_file, args.tmp_dir)
        logger.info("Save local file %s", hdr_local)

        hls_converter = ConvertHls(hdf_local)

        output_dir = os.path.join(
            args.output_dir,
            args.type,
            str(year),
            tile[:2],
            tile[2],
            tile[3],
            tile[4]
        )
        hls_converter.start(output_dir=output_dir)

        os.remove(hdf_local)
        os.remove(hdr_local)
        break




if __name__ == '__main__':
    main()