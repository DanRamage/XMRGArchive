import os
import glob
import optparse
import configparser
import geojson
import logging.config
from datetime import datetime, timedelta
from dateutil.parser import parse as du_parse
from nfs_mount_utils import check_mount_exists, mount_nfs, test_docker_host_volume
from archive_utilities import xmrg_archive_utilities

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOGFILES_DIRECTORY = ".\logfiles"


import sys
sys.path.append("./debug/pydevd-pycharm.egg")
import pydevd_pycharm
pydevd_pycharm.settrace('host.docker.internal',
                        port=4200,
                        stdoutToServer=True,
                        stderrToServer=True)
logger = None
def missing_data_scan(base_url,
                      scan_directory,
                      start_date,
                      end_date,
                      check_file_datetimes,
                      repository_data_duration_hours):
    results = {}
    xmrg_utils = xmrg_archive_utilities(scan_directory)
    results = xmrg_utils.scan_for_missing_data(start_date, end_date)
    #If we want to check if the source files are newer than what we downloaded.
    if check_file_datetimes:
        #check_file_timestamps(self, base_url, from_date, to_date)
        xmrg_utils.check_file_timestamps(base_url, start_date, end_date, repository_data_duration_hours)

    return results

def validate_mount(server, remote_path, local_mount_point):
    if not check_mount_exists(local_mount_point):
        return mount_nfs(server, remote_path, local_mount_point)
    return True

def fill_xmrg_gaps(base_url, base_archive_directory: str, files_to_fill: {}):
    xmrg_utils = xmrg_archive_utilities(base_archive_directory)
    for year in files_to_fill:
        for month in files_to_fill[year]:
            xmrg_utils.download_files(base_url, files_to_fill[year][month])


def main():
    parser = optparse.OptionParser()

    parser.add_option("--ConfigFile", dest="config_file",
                      help="Configuration file for the script.")
    parser.add_option("--LogConfigFile", dest="log_config_file",
                      help="Logging configuration file.")
    parser.add_option("--FillGaps", dest="fill_gaps",
                      help="Will look and fill gaps from the last 72 hours. Currently "\
                        "the SERFC web directory only keeps last 72 hours of data.",
                        action="store_true", default=False)
    parser.add_option("--MissingFilesReport", dest="missing_files_report",
                      help="Flag that will go through the archive directories and check if there are"
                           "missing files.", action="store_true", default=False)
    parser.add_option("--StartDate", dest="start_date",
                      help="Date to start processing.", default=datetime.now() - timedelta(hours=72))
    parser.add_option("--EndDate", dest="end_date",
                      help="Date to start processing.", default=datetime.now())

    (options, args) = parser.parse_args()

    config_file = configparser.ConfigParser()
    config_file.read(options.config_file)

    logging.config.fileConfig(options.log_config_file)
    logger = logging.getLogger(__name__)

    logger.info("Log file opened.")

    #Get NFS settings
    nfs_server = config_file.get("nfs", "nfs_server_ip")
    nfs_share = config_file.get("nfs", "nfs_directory")
    local_mount = config_file.get("nfs", "local_mount_directory")

    #Get HTTP download url
    base_url = config_file.get("xmrg", "download_url")
    #Get the number of hours of historical data stored at the endpoint.
    repository_data_duration_hours = config_file.getint("xmrg", "remote_repository_data_duration_hours")
    start_date = options.start_date
    if type(start_date) != datetime:
        start_date = du_parse(options.start_date)
    end_date = options.end_date
    if type(end_date) != datetime:
        end_date = du_parse(options.end_date)
    base_xmrg_directory = config_file.get("directories", "xmrg_data_directory")
    #if validate_mount(nfs_server, nfs_share, local_mount):
    check_file_timestamps = True
    if test_docker_host_volume(local_mount):
        if options.missing_files_report:
            year_list = []
            missing_data_scan(base_url,
                              base_xmrg_directory,
                              start_date,
                              end_date,
                              check_file_timestamps,
                              repository_data_duration_hours)
        if options.fill_gaps:
            results = missing_data_scan(base_url,
                                        base_xmrg_directory,
                                        start_date,
                                        end_date,
                                        check_file_timestamps,
                                        repository_data_duration_hours)
            logger.info(f"The following files are missing between: {start_date.strftime('%Y-%m-%d %H:%M:%S''')} and "
                        f"{end_date.strftime('%Y-%m-%d %H:%M:%S''')}: {results}")
            fill_xmrg_gaps(base_url, base_xmrg_directory, results)


    return

if __name__ == "__main__":
    main()