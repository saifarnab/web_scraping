import logging
import random
import subprocess
import time

from bs4 import BeautifulSoup
import pandas as pd
import requests

# install dependencies
subprocess.check_call(['pip', 'install', 'beautifulsoup4'])
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'requests'])

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def get_request_headers() -> dict:
    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36'}


def convert_runtime(time_str):
    if len(time_str) == 2:
        return f"{60}"
    if "h" not in time_str.lower():
        return time_str[: len(time_str) - 1]
    hours, minutes = time_str.split("h ")
    minutes = int(minutes[:-1])
    total_minutes = int(hours) * 60 + minutes
    return total_minutes


def run():
    logging.info('Script Start running ...')
    df = pd.read_csv('new.csv')
    ids = df['0']
    data = []
    for ind, each_id in enumerate(ids):
        try:
            url = f"https://m.imdb.com/title/{each_id}/"
            page = requests.post(url, headers=get_request_headers())
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, "html.parser")
                title = soup.find('span', class_="sc-afe43def-1 fDTGTb").text
                ul = soup.find('ul',
                               class_='ipc-inline-list ipc-inline-list--show-dividers sc-afe43def-4 kdXikI baseAlt')
                lis = ul.findAll('li', class_="ipc-inline-list__item")

                print(lis)

                if len(lis) == 4:
                    data.append(
                        [title.strip(), lis[0].text.strip(), convert_runtime(lis[3].text.strip()), lis[1].text.strip().replace('–', '-'),
                         each_id])

                elif len(lis) == 2:
                    if 'tv' in lis[0].text.strip().lower():
                        data.append(
                            [title.strip(), lis[0].text.strip(), convert_runtime(lis[1].text.strip()), 'N/A', each_id])
                    else:
                        data.append([title.strip(), 'N/A', convert_runtime(lis[1].text.strip()), lis[0].text.strip().replace('–', '-'), each_id])

                logging.info(f'--> data is extracted for id = {each_id}')

        except Exception as ex:
            print(ex)
            logging.error(f'--> failed to extract data from id = {each_id}')
            continue

    df = pd.DataFrame(data, columns=["Title", "MediaType", "RunTime", "Year", "ImdbID"])
    df.to_csv(f"data-{random.randint(1, 9999)}.csv", index=False, encoding='utf8')
    logging.info('Script successfully completed!')


run()
