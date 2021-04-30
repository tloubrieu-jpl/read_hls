# Work with HLS data

This package enables:
 - Read HLS v1.4 data
 - Download HLS data and convert them in netCDF4
 - Deploy as a kubernetes job
 

## Pre-requisites

Use conda 

## Install

Virtual environment

    conda create --name hls
    conda activate hls
    conda install --file requirements_conda.txt
    pip install requirements.txt

## Run 

Download HLS data and convert them to netcdf4: 

    python ./download_convert_tile.py --help
    

## Create the docker image

    docker build . -t tloubrieu/hls_download_convert
    docker login
    docker push tloubrieu/hls_download_convert

## Run on MOC cluster as a kubernetes job

You need to log in a MOC cluster.

Create a persistent volume to host the converted data:

    kubectl create -f persistent_storage.yaml -n sdap
    
Launch the job:

    kubectl apply -f job.yaml -n sdap



    
    
 