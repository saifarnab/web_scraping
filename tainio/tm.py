import threading
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from lxml import etree
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# disable ssl warning
urllib3.disable_warnings()


def config_driver() -> webdriver.Chrome:
    options = Options()
    # options.add_argument("--headless")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/96.0.4664.45 Safari/537.36')
    options.add_argument("window-size=1024,768")
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
    def __init__(self, url, num_threads=4):
        self.url = url
        self.num_threads = num_threads
        self.file_size = int(requests.head(url, verify=False).headers["Content-Length"])
        self.chunk_size = self.file_size // self.num_threads
        self.lock = threading.Lock()
        self.bytes_written = 0
        self.filename = url.split("/")[-1]

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
        print(f'File size is {int(self.file_size / 1024000)}mb approximately. Start downloading...')
        print('Start downloading...')
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
        print(f"Request completed in {(time.time() - start) * 1000} seconds")
        print("Download successful!")


def get_request_headers() -> dict:
    user_agent_gen = generate_user_agent(os=['linux', 'mac'])
    header = ({'User-Agent': f'{user_agent_gen}', 'Accept-Language': 'en-US, en;q=0.5'})
    return header


def get_break_pointer(url: str):
    while True:
        webpage = requests.get(url, headers=get_request_headers())
        if 'checkcaptcha' in webpage.url:
            print('captcha issue occurred...')
            continue
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))
        movie_cards = dom.xpath('//div[@id="dle-content"]//a[@class="entryLink"]')
        return f'{movie_cards[6].text}'


def get_detail_page_links(break_pointer: str):
    downloadable_items = []
    page = 1
    while True:
        url = f'https://tainio-mania.online/page/{page}/'
        webpage = requests.get(url, headers=get_request_headers())
        if 'checkcaptcha' in webpage.url:
            print('captcha issue occurred...')
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


def get_video_link(url='https://tainio-mania.online/load/seir/walker-2021/21-1-0-25272'):
    driver = config_driver()
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="fake-player-btnplay"]')))
    driver.find_element(By.XPATH, '//div[@id="fake-player-btnplay"]').click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//iframe[1]')))
    iframe = driver.find_element(By.XPATH, '//iframe[1]')
    driver.switch_to.frame(iframe)
    time.sleep(10000)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//iframe[@id='pjsfrrsplayer22serial']")))

    time.sleep(10000)
    driver.find_element("//iframe[@id='pjsfrrsplayer22serial']").click()
    time.sleep(10000)

    # switch to the iframe
    iframe = driver.find_element("//iframe[@id='pjsfrrsplayer22serial']")
    driver.switch_to.frame(iframe)
    print('switch to iframe')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//pjsdiv[@style="display: block; transition: height 0.1s ease-out 0s; font-size: 15px; height: 0px; overflow-y: scroll; margin-right: 0px; max-height: 377px; border-top: none;"]//pjsdiv')))
    print('found')
    # driver.find_element(By.XPATH, '//pjsdiv[@class="pjsplplayer22serialscroll"]').click()
    time.sleep(100000000)


def run(path: str):
    # url = 'https://www.cdn.vidce.net/d/t7hT1KB9aNksT_JMVhC58Q/1684214312/video/Devs/1x01.mp4'
    # downloader = Downloader(url, num_threads=10)
    # downloader.start()
    downloadable_items = get_detail_page_links(get_break_pointer('https://tainio-mania.online'))
    print(downloadable_items)


if __name__ == '__main__':
    # dwnld_path = str(input('Enter full path of output folder: ')).strip()
    # if dwnld_path in [None, '']:
    #     print('Invalid path')
    # run('')
    get_video_link()
