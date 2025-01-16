import logging
import os
import glob
import string
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from nfs_mount_utils import check_mount_exists, mount_nfs

from xmrgprocessing.xmrg_utilities import build_filename, get_collection_date_from_filename
from xmrgprocessing.xmrg_utilities import http_download_file

class xmrg_archive_utilities:
    def __init__(self, archive_directory):
        self._logger = logging.getLogger()
        self._parent_directory = archive_directory
        self._data_path_template = string.Template("$year/$month")

    def build_file_list_for_date_range(self, start_date, end_date, file_ext):
        date_time_list = []
        date_time = start_date
        while date_time < end_date:
            file_name = build_filename(date_time, file_ext)
            date_time += timedelta(hours=1)
            date_time_list.append(file_name)
        return date_time_list

    def file_list(self, year, month_abbreviation):
        '''
        Given the year and month, return a directory listing of the files there.
        :param year:
        :param month_abbreviation:
        :return:
        '''
        path_to_check = self._data_path_template.substitute(year=year, month=month_abbreviation)
        path_to_check = os.path.join(self._parent_directory, path_to_check)
        file_ext = "gz"
        file_filter = os.path.join(path_to_check, f"*.{file_ext}")
        file_list = glob.glob(file_filter)
        #We might not have the .gz files, so let's search just for files.
        if len(file_list) == 0:
            file_ext = ""
            file_filter = os.path.join(path_to_check, "*")
            file_list = glob.glob(file_filter)
        return file_list

    def scan_for_missing_data(self, from_date, to_date):
        '''

        :param from_date:
        :param to_date:
        :return:
        '''
        results = {}
        date_time = from_date
        #Build a list of the files we should have for a given date range.
        complete_file_list = self.build_file_list_for_date_range(from_date, to_date, "")
        complete_file_set = set(complete_file_list)
        while date_time < to_date:
            year = date_time.year
            month_str = date_time.strftime("%b")
            #Get all the files available for the given year/month
            file_list = self.file_list(year, month_str)
            #Get file names only
            file_name_list = []
            for file in file_list:
                file_dir, file_name = os.path.split(file)
                #We just want the name of the file with no extensions.
                file_name, exten = os.path.splitext(file_name)
                file_name_list.append(file_name)
            end_date_time = date_time + relativedelta(months=1)
            #end_date_time = date_time + relativedelta(hours=1)

            archive_file_set = set(file_name_list)
            missing_files = complete_file_set.difference(archive_file_set)
            if len(missing_files):
                if year not in results:
                    results[year] = {}
                if month_str not in results[year]:
                    results[year][month_str] = []
                results[year][month_str].extend(list(missing_files))
            date_time = end_date_time
        return results

    def download_files(self, base_url: str, file_list: []):
        '''

        :param base_url:
        :param download_directory:
        :param file_list:
        :return:
        '''

        for xmrg_file in file_list:
            file_datetime = datetime.strptime(get_collection_date_from_filename(xmrg_file), "%Y-%m-%dT%H:00:00")

            year = file_datetime.year
            month_abbr = file_datetime.strftime("%b")

            download_path = self._data_path_template.substitute(year=year, month=month_abbr)
            download_path = os.path.join(self._parent_directory, download_path)
            if not os.path.exists(download_path):
                self._logger.info(f"Directory: {download_path} does not exist, creating it.")
                try:
                    os.makedirs(download_path, exist_ok=False)
                except FileExistsError as e:
                    self._logger.error(f"Directory {download_path} already exists, skipping. {e}")
            file_ext = "gz"
            #Check if the path we want to download to exists. Data is stored in a /year/month
            #directory structure.
            dl_xmrg_filename = f"{xmrg_file}.{file_ext}"
            self._logger.info(f'Downloading xmrg file: {dl_xmrg_filename}')
            xmrg_file = http_download_file(base_url, dl_xmrg_filename, download_path)
            if xmrg_file is None:
                self._logger.error(f'Failed to download xmrg file: {dl_xmrg_filename}')
            else:
                self._logger.info(f'Successfully downloaded xmrg file: {dl_xmrg_filename}')
        return
