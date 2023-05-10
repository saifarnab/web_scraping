import os
import threading
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from user_agent import generate_user_agent

# disable ssl warning
urllib3.disable_warnings()

# define output folder path, must include the tail '/' or '\'
OUTPUT_FOLDER_PATH = '/home/dfs/Documents/web_scraping/tainio/downloads/'


def config_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.page_load_strategy = 'eager'
    options.add_argument(f'user-agent={generate_user_agent()}')
    options.add_argument("lang=en-GB")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


class Downloader:
    def __init__(self, url, name, num_threads=4):
        self.url = url
        self.num_threads = num_threads
        self.file_size = int(requests.head(url, verify=False).headers["Content-Length"])
        self.chunk_size = self.file_size // self.num_threads
        self.lock = threading.Lock()
        self.bytes_written = 0
        self.filename = OUTPUT_FOLDER_PATH + name

    def download(self, start_byte, end_byte):
        headers = {"Range": f"bytes={start_byte}-{end_byte}"}
        res = requests.get(self.url, headers=headers, stream=True, verify=False)

        with self.lock:
            with open(self.filename, "r+b") as f:
                f.seek(start_byte)
                f.write(res.content)

            self.bytes_written += end_byte - start_byte

    def start(self):
        start = time.time()
        print(f'File size is {int(self.file_size / 1024000)}mb approximately. Downloading...')
        with open(self.filename, "wb") as f:
            f.truncate(self.file_size)

        threads = []

        for i in range(self.num_threads):
            start_byte = i * self.chunk_size
            end_byte = (i + 1) * self.chunk_size - 1 if i < self.num_threads - 1 else self.file_size - 1
            thread = threading.Thread(target=self.download, args=(start_byte, end_byte))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        print(f"Download completed in {int((time.time() - start))} seconds approximately")


def get_request_headers() -> dict:
    user_agent_gen = generate_user_agent(os=['linux', 'mac'])
    header = ({'User-Agent': f'{user_agent_gen}', 'Accept-Language': 'en-US, en;q=0.5'})
    return header


def reverse_list(arr):
    left = 0
    right = len(arr) - 1
    while left < right:
        temp = arr[left]
        arr[left] = arr[right]
        arr[right] = temp
        left += 1
        right -= 1

    return arr


def get_break_pointer(url: str) -> str:
    while True:
        try:
            webpage = requests.get(url, headers=get_request_headers())
            if 'checkcaptcha' in webpage.url:
                print('Captcha issue occurred, retrying..')
                continue
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))
            movie_cards = dom.xpath('//div[@id="dle-content"]//a[@class="entryLink"]')
            return f'{movie_cards[0].text.strip()}'
        except Exception as e:
            continue


def get_detail_page_links(break_pointer: str):
    downloadable_items = []
    page = 1
    while True:
        url = f'https://tainio-mania.online/page/{page}/'
        webpage = requests.get(url, headers=get_request_headers())
        if 'checkcaptcha' in webpage.url:
            print('Captcha issue occurred, retrying..')
            continue
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))
        titles = dom.xpath('//div[@id="dle-content"]//a[@class="entryLink"]')
        links = dom.xpath('//div[@id="dle-content"]//a[@class="entryLink"]/@href')

        for title, link in zip(titles, links):
            if title.text.strip() == break_pointer:
                return downloadable_items
            downloadable_items.append({'title': title.text.strip(), 'link': link.strip()})

        page += 1


def get_video_link(url='https://tainio-mania.online/load/seir/deep-shit-2021/21-1-0-32979'):
    for i in range(5):
        try:
            driver = config_driver()
            driver.get(url)
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@id="fake-player-btnplay"]')))
            driver.find_element(By.XPATH, '//div[@id="fake-player-btnplay"]').click()

            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//iframe[1]')))
            iframe = driver.find_elements(By.XPATH, '//iframe')[0]
            iframe.click()
            time.sleep(3)
            driver.switch_to.frame(iframe)
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//video')))
            video = driver.find_element(By.XPATH, '//video').get_attribute('src')

            # check movie or series
            checker = video.split('/')[-1].split('.')[0]
            if 'x' not in checker:
                return video

            print('Detected as a series, finding which episode of which season to download')

            # check max series
            season = 1
            while True:
                temp = f'{season}x01'
                link = video.replace(checker, temp)
                response = requests.head(link, verify=False, headers=get_request_headers())
                if 'checkcaptcha' in response.url:
                    print('Captcha issue occurred, retrying..')
                    continue
                if response.status_code != 200:
                    break
                season += 1

            valid_season = season - 1

            # check max episode
            episode = 1
            while True:
                if episode <= 9:
                    temp = f'{valid_season}x0{episode}'
                else:
                    temp = f'{valid_season}x{episode}'
                link = video.replace(checker, temp)
                response = requests.head(link, verify=False, headers=get_request_headers())
                if 'checkcaptcha' in response.url:
                    print('Captcha issue occurred, retrying..')
                    continue
                if response.status_code != 200:
                    break
                episode += 1

            valid_episode = episode - 1
            if valid_episode <= 9:
                valid_episode = f'0{valid_episode}'
            return video.replace(checker, f'{valid_season}x{valid_episode}'), f'{valid_season}x{valid_episode}'
        except Exception as e:
            print('Exception occurs, retrying...')
            continue
    return None, None


def run():
    print('Script starts running ...')
    break_pointer = get_break_pointer('https://tainio-mania.online')
    print(f'Content will be downloaded next to this `{break_pointer}`')
    while True:
        downloadable_items = reverse_list(get_detail_page_links(break_pointer))
        if len(downloadable_items) < 1:
            print('No new content available to download, waiting 5 minutes for next try..')
            time.sleep(300)
            continue

        for content in downloadable_items:
            print(f'Fetch video download link for -> {content["title"]}')
            link, name = get_video_link(content['link'])
            if link is None:
                print(f'`{content["title"]}` -> failed to generate downloadable link, moving next..')
                continue
            try:
                downloader = Downloader(link, f'{str(content["title"]).replace("/", " ")}_{name}', num_threads=3)
                downloader.start()

            except Exception as e:
                print(f'`{content["title"]}` -> failed to download this content, moving next..')

        break_pointer = downloadable_items[0]['title']


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_FOLDER_PATH):
        print('Invalid output folder path')
    else:
        run()
