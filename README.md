# Overview

<p>This utility keeps the XMRG archive we have locally as up to date as possible. 
Currently the SERFC site only holds the past 72 hours of NEXRAD datas in XMR format. 
This utility is scheduled to run at an interval. With no user provided start/end date, 
it will check our local archive to see if any files from the past 72 hours are missing and will download. 
It will also check to see if files we have are older than the same remote file and if so re-download it. 
There is a periodic QAQC that goes on with the remote data.</p>

## Command Line Parameters
**--ConfigFile** - Full Path to the configuration file, this is a required parameter. 

**--LogConfigFile** - Full path the to logging configuration file. This is a required parameter.

**--FillGaps** - If set, this flag will attempt to fill any missing files between
    the StartDate and EndDate parameters below.

**--MissingFilesReport** - If set, this flag will produce a report of what files are missing for the 
    date range in the StartDate and EndDate parameters below.

**--StartDate** - Date/Time string to begin our operations.

**--EndDate** - Date/Time string to end our operations.

## Configuration File(--ConfigFile)
The ConfigFile parameter loads an ini file that has the following entries.

**[nfs]**<br>
nfs_server_ip= If the utility is not running in a Docker, this is the address for the NFS share of the archive.<br>
nfs_directory=If the utility is not running in a Docker, this is the name of the NFS share.<br>

**[directories]**<br>
local_mount_directory=Whether in a Docker or not, this is the base directory. In a Docker, this directory would be a 
    volume to the host machine.<br>
xmrg_data_directory = This is full path to the base directory for XMRG data.<br>

**[xmrg]**<br>
download_url=The url to the XMRG data.<br>
remote_repository_data_duration_hours=This is the number of hours the remote repository keeps on hand, 
    anything older rolls off. For SERFC, it's 72 hours<br>


## Logging Configuration File(--LogConfigFile)
This is a standard python logging .conf file. 

In a Docker, the directory to write the logfiles to should be an attached volume, and the filehandler path
in the logging .conf file should be relative to that.


# Docker configuration
** Sample Build Command ** <br>
    sudo docker build -t xmrg-archive-docker .
    <br>
** Sample Run Command **<br>
    docker run -v /mnt/xmrg_nfs:/xmrg_nfs -v /tmp:/logfiles xmrg-archive-docker --ConfigFile=/config/xmrg_archive_config_docker.ini --LogConfigFile=/config/xmrg_archive_logging_docker.conf --FillGaps
    <br>