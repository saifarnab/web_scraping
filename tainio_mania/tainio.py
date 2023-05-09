import threading
import time

import requests
import urllib3
from bs4 import BeautifulSoup
from lxml import etree
from user_agent import generate_user_agent

# disable ssl warning
urllib3.disable_warnings()


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


def get_latest_pointer(url: str):
    while True:
        webpage = requests.get(url, headers=get_request_headers())
        if 'checkcaptcha' in webpage.url:
            print('captcha issue occurred...')
            continue
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))
        movie_cards = dom.xpath('//div[@id="dle-content"]//a[@class="entryLink"]')
        upload_times = dom.xpath('//div[@id="dle-content"]//div[@class="time_stamps"]//span[2]')
        return f'{movie_cards[0].text}-{upload_times[0].text}'


def get_detail_page_links(break_pointer: str):
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
        upload_times = dom.xpath('//div[@id="dle-content"]//div[@class="time_stamps"]//span[2]')

        for title, link, upload_time in zip(titles, links, upload_times):
            print(f'{title.text}-{link}-{upload_time.text}')
        page += 1


def run():
    # url = 'https://www.cdn.vidce.net/d/t7hT1KB9aNksT_JMVhC58Q/1684214312/video/Devs/1x01.mp4'
    # downloader = Downloader(url, num_threads=10)
    # downloader.start()
    get_detail_page_links(get_latest_pointer('https://tainio-mania.online'))


if __name__ == '__main__':
    run()
