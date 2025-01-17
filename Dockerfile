FROM python:3.11
LABEL authors="danramage"

#We are writing out to a NAS or other storage device via an NFS mount. We need to set
#The UID and GID of the docker to be one that can access the mount.
ARG UID=1001
ARG GID=1004
# Create a new user with the specified UID and GID
RUN groupadd -g ${GID} python_flask && \
    useradd -u ${UID} -g python_flask -m xeniaprod

# Create directories as root and change ownership to the non-root user
RUN mkdir -p /logfiles /xmrg_nfs && \
    chown -R ${UID}:${GID} /logfiles /xmrg_nfs


# Set the user to use when running the image
USER xeniaprod



RUN pip install geojson
RUN pip install dateparser
RUN pip install git+https://github.com/DanRamage/xmrgprocessing.git
RUN pip install pydevd_pycharm

ADD main.py .
ADD archive_utilities.py .
ADD nfs_mount_utils.py .

COPY config/ config/

ENTRYPOINT ["python", "./main.py"]
