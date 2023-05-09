import ssl
import threading
import time

import requests

import urllib3
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
        print(f'File size is {int(self.file_size/1024000)}mb approximately. Start downloading...')
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


if __name__ == '__main__':
    url = 'https://www.cdn.vidce.net/d/t7hT1KB9aNksT_JMVhC58Q/1684214312/video/Devs/1x01.mp4'
    downloader = Downloader(url, num_threads=10)
    downloader.start()
