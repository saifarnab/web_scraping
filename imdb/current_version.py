import logging
import random
import subprocess
import time

from bs4 import BeautifulSoup
import pandas as pd
import requests

class GetErrorIDs:
    """
    Class to scrape runtime, title and other information given an IMDb ID 
    """

    def __init__(self, id_, verbose = False):
        self.id_ = id_
        self.verbose = verbose

    def get_request_headers(self) -> dict:
        return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/50.0.2661.102 Safari/537.36'}

    def convert_runtime(self, time_str):
        if len(time_str) == 2:
            return f"{60}"
        if "h" not in time_str.lower():
            return time_str[: len(time_str) - 1]
        hours, minutes = time_str.split("h ")
        minutes = int(minutes[:-1])
        total_minutes = int(hours) * 60 + minutes
        return total_minutes

    def run(self):
        # logging.info('Script Start running ...')
        # df = pd.read_csv('ids to scrape.csv')
        # ids = df['0']
        data = []
        # for ind, each_id in enumerate(ids):
        try:
            url = f"https://m.imdb.com/title/{self.id_}/"
            page = requests.post(url, headers = self.get_request_headers())
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, "html.parser")
                title = soup.find('span', class_="sc-afe43def-1 fDTGTb").text
                ul = soup.find('ul',
                               class_='ipc-inline-list ipc-inline-list--show-dividers sc-afe43def-4 kdXikI baseAlt')
                lis = ul.findAll('li', class_="ipc-inline-list__item")
                if len(lis) == 4:
                    data.append(
                        [title.strip(), lis[0].text.strip(), self.convert_runtime(lis[3].text.strip()), lis[1].text.strip().replace('–', '-'),
                         self.id_])

                elif len(lis) == 3:
                    data.append([title.strip(), lis[0].text.strip(), 'N/A', lis[1].text.strip().replace('–', '-'), self.id_])

                elif len(lis) == 2:
                    if 'tv' in lis[0].text.strip().lower():
                        data.append(
                            [title.strip(), lis[0].text.strip(), self.convert_runtime(lis[1].text.strip()), 'N/A', self.id_])
                    else:
                        data.append([title.strip(), 'N/A', self.convert_runtime(lis[1].text.strip()), lis[0].text.strip().replace('–', '-'), self.id_])

                # logging.info(f'--> data is extracted for id = {self.id_}')

        except Exception as ex:
            # logging.error(f'--> failed to extract data from id = {self.id_}')
            if self.verbose:
                print(f'--> failed to extract data from id = {self.id_}', type(ex), ex)
            return None

        try:
            runtime = int(data[0][2])
        except:
            runtime = None

        # print('Corrected data: ', data)
        try:
            return {'title': data[0][0],
                   'media_type': data[0][1],
                   'runtime': runtime,
                   'release_year': data[0][3],
                   'imdb_id': data[0][4]}
        except Exception as e:
            if self.verbose:
                print(type(e), e)
                print(data)
            return {'title': None,
                   'media_type': None,
                   'runtime': None,
                   'release_year': None,
                   'imdb_id': None}



if __name__ == '__main__':

    # Read CSV of missing IDs
    df_missing = pd.read_csv('new_missing.csv')

    # Loop through each ID and scrape its information
    results = []
    for id_ in df_missing.imdb_id.values:
        res = GetErrorIDs(id_).run()
        results.append(res)
    # Create a dataframe out of the results and save to local file
    pd.DataFrame(results).to_csv('output.csv', index = False)
