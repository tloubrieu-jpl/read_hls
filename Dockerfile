FROM continuumio/anaconda3
MAINTAINER Andrew Jiang <andrew.h.jiang@jpl.nasa.gov>

RUN mkdir -p /app
WORKDIR /app
COPY download_convert_tile.py .
COPY convert_hls.py .
COPY requirements.txt .
RUN conda install -c conda-forge pyhdf
RUN python -m pip install -r requirements.txt

CMD ["python", "download_convert_tile.py", "--type", "S30", "--years", "2015",  "--tiles", "18TYN", "--tmp-dir", "/tmp", "--output-dir", "/data/"]

