import os
import random
import re
import time
import urllib.parse
from functools import cached_property

import requests
from bs4 import BeautifulSoup
from utils import JSONFile, Log, Time, TimeFormat

log = Log('GenericDownloader')


class GenericDownloader:
    BASE_URL = 'https://www.dmc.gov.lk'
    N_MAX_DOWNLOADS = 1 if os.name == 'nt' else 100

    def __init__(self, doc_type: str, report_type_id: str):
        self.doc_type = doc_type

        self.report_type_id = report_type_id

    @property
    def dir_data(self):
        dir_data = os.path.join('data', self.doc_type)
        if not os.path.exists(dir_data):
            os.makedirs(dir_data)
        return dir_data

    @property
    def url(self):
        d = dict(
            option='com_dmcreports',
            view='reports',
            limit=0,
            search='',
            report_type_id=self.report_type_id,
            fromdate='2014-05-31',
            todate='2024-05-31',
            lang='en',
        )

        return '{}/index.php?{}'.format(
            GenericDownloader.BASE_URL, urllib.parse.urlencode(d)
        )

    @cached_property
    def html(self):
        return requests.get(self.url, verify=False).text

    @staticmethod
    def parse_date_str(date_str):
        date_str = date_str.strip()
        try:
            format = TimeFormat('%Y-%m-%d %H:%M')
            return format.parse(date_str).ut
        except BaseException:
            format2 = TimeFormat('%Y-%m-%d')
            return format2.parse(date_str).ut

    @staticmethod
    def parse_name_str(name):
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        name = name.replace(' ', '-')
        return name.lower()

    def get_link_info_list(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        elem_table = soup.find('table', {'class': 'mtable'})
        d_list = []
        for elem_tr in elem_table.find_all('tr')[1:]:
            elem_tds = elem_tr.find_all('td')
            name = elem_tds[0].text
            time_str = elem_tds[1].text + ' ' + elem_tds[2].text
            ut = self.parse_date_str(time_str)
            time_id = TimeFormat('%Y%m%d.%H%M').format(Time(ut))
            href = GenericDownloader.BASE_URL + elem_tds[-1].find('a')['href']
            ext = href.split('.')[-1]
            d = dict(
                name=name,
                time_str=time_str,
                time_id=time_id,
                ut=ut,
                href=href,
                ext=ext,
            )
            d_list.append(d)
        n = len(d_list)
        log.info(f'Found {n} links.')

        data_path = os.path.join(self.dir_data, 'info.json')
        JSONFile(data_path).write(d_list)
        log.info(f'Wrote {data_path}')
        return d_list

    def download_binary(url, file_path):
        with open(file_path, 'wb') as f:
            f.write(requests.get(url, verify=False).content)
        t_sleep = random.random()
        log.debug(f"😴 {t_sleep:.2f}s")
        time.sleep(t_sleep)

    @staticmethod
    def get_file_path(dir_data, link_info):
        name_str = GenericDownloader.parse_name_str(link_info['name'])
        file_path = os.path.join(
            dir_data,
            f"{link_info['time_id']}.{name_str}.{link_info['ext']}",
        )
        return file_path

    def download_all(self):
        link_info_list = self.get_link_info_list()
        n_downloaded = 0
        n_total = len(link_info_list)
        for i_link, link_info in enumerate(link_info_list, start=1):
            file_path = GenericDownloader.get_file_path(
                self.dir_data, link_info
            )
            if os.path.exists(file_path):
                log.debug(f"{file_path} exists.")
                continue

            GenericDownloader.download_binary(link_info['href'], file_path)
            n_downloaded += 1
            log.info(
                f"{i_link}/{n_total})"
                + f" Downloaded {file_path} ({n_downloaded})"
            )

            if n_downloaded >= GenericDownloader.N_MAX_DOWNLOADS:
                break
