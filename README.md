# Read HLS data

## Pre-requisites

Use conda 

Get data from HLS, for example:

https://hls.gsfc.nasa.gov/data/v1.4/L30/2021/01/U/D/T/HLS.L30.T01UDT.2021001.v1.4.hdf
https://hls.gsfc.nasa.gov/data/v1.4/L30/2021/01/U/D/T/HLS.L30.T01UDT.2021001.v1.4.hdf.hdr

## Install

Virtual environment

    conda create --name hls
    conda activate hls
    conda install --file requirements_conda.txt
    pip install requirements.txt

## Change the path to your hdf file

In read_hls.py


# Run

    python read_hls.py
 