FROM python:3.11
LABEL authors="danramage"

RUN pip install geojson
RUN pip install dateparser
RUN pip install git+https://github.com/DanRamage/xmrgprocessing.git
RUN pip install pydevd_pycharm

ADD main.py .
ADD archive_utilities.py .
ADD nfs_mount_utils.py .

COPY config/ config/
#This directory is empty when we copy, but we are just making sure we'll have the
#directory to write the logfiles in to keep things clean.
COPY logfiles/ logfiles/

RUN mkdir -p /xmrg_nfs


ENTRYPOINT ["python", "./main.py"]
#ENTRYPOINT ["python", "main.py"]
#ENTRYPOINT ["top", "-b"]