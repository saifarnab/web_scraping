import os
import subprocess
import time
import pandas as pd

import requests
import urllib3
from pySmartDL import SmartDL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

# install dependencies
subprocess.check_call(['pip', 'install', 'pySmartDL'])
subprocess.check_call(['pip', 'install', 'user_agent'])
subprocess.check_call(['pip', 'install', 'urllib3'])
subprocess.check_call(['pip', 'install', 'pandas'])

# define output folder path, must include the tail '/' or '\'
# OUTPUT_FOLDER_PATH = 'C:\tool_downloads' # for windows
OUTPUT_FOLDER_PATH = 'Z:\\'  # for linux & mac
TRACKER_CSV_PATH = 'tracker.csv'

urllib3.disable_warnings()


def config_driver():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("lang=en-GB")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.minimize_window()
    return driver


def handle_freeze(driver):
    try:
        print('Handling captcha perimeter X')
        open_window_elem = '//a[@style="display: block"]'
        driver.find_element(By.XPATH, open_window_elem).click()
        # ActionChains(driver).move_to_element(open_window_elem).click(open_window_elem).perform()
        time.sleep(2)
    except Exception as e:
        print(e)


def csv_init():
    df = pd.DataFrame(columns=['Files'])
    df.to_csv(TRACKER_CSV_PATH, index=False)
    print('Tracker csv init success')


def inset(content_name: str):
    df = pd.read_csv(TRACKER_CSV_PATH)
    name_exists = content_name in df['Files'].values
    if name_exists:
        return True
    new_data = {'Files': content_name.strip()}
    df = df.append(new_data, ignore_index=True)
    df.to_csv(TRACKER_CSV_PATH, index=False)
    print(f'Data inserted successfully into {TRACKER_CSV_PATH}.')


def download_manager(filename, url: str):
    special_char_list = ["$", "@", "#", "&", "%", ":", "/", "\\", "^", "!", "(", ")", "<", ">", "{", "}", "[", "]", "|"]
    for item in special_char_list:
        if item in filename:
            filename = filename.replace(item, "")

    filename = filename.replace(' ', '_')
    dest = OUTPUT_FOLDER_PATH + filename
    if os.path.exists(dest) is True:
        print('Content already available, moving next..')
        return

    print('Content downloading ...')
    smart_dwnld_manager = SmartDL(url, dest, verify=False, threads=15)
    smart_dwnld_manager.start()


def get_request_headers() -> dict:
    return ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 '
                           'Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})


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


def handle_captcha(driver):
    driver.get('https://tainio-mania.online/checkcaptcha/')
    print('Website have blocked you IP, please solve the captcha.')
    time.sleep(120)
    # WebDriverWait(driver, 3600).until(EC.visibility_of_element_located((By.XPATH, '//a[@id="go2full"]')))
    driver.find_element(By.XPATH, '//a[@id="go2full"]').click()
    time.sleep(2)


def get_break_pointer(driver, url: str):
    while True:
        try:
            driver.get(url)
            time.sleep(1)
            if 'checkcaptcha' in driver.current_url:
                handle_captcha(driver)
                continue
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@id="dle-content"]//a[@class="entryLink"]')))
            cards = driver.find_elements(By.XPATH, '//div[@id="dle-content"]//a[@class="entryLink"]')
            return f'{cards[1].text.strip()}'
        except Exception as e:
            print('Website not responding, retrying...')
            time.sleep(10)
            continue


def get_detail_page_links(driver, break_pointer: str):
    downloadable_items = []
    page = 1
    while True:
        url = f'https://tainio-mania.online/page/{page}/'
        driver.get(url)
        time.sleep(1)
        if 'checkcaptcha' in driver.current_url:
            handle_captcha(driver)
            continue

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@id="dle-content"]//a[@class="entryLink"]')))
        items = driver.find_elements(By.XPATH, '//div[@id="dle-content"]//a[@class="entryLink"]')

        for item in items:
            if item.text.strip() == break_pointer:
                return downloadable_items
            downloadable_items.append({'title': item.text.strip(), 'link': item.get_attribute('href')})

        page += 1


def get_video_link(driver, url):
    for i in range(5):
        try:
            driver.get(url)
            time.sleep(2)
            if 'checkcaptcha' in driver.current_url:
                handle_captcha(driver)
                continue
            # handle_freeze(driver)
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@id="fake-player-btnplay"]')))
            btn_play = driver.find_element(By.XPATH, '//div[@id="fake-player-btnplay"]')
            driver.execute_script("arguments[0].click();", btn_play)
            time.sleep(3)
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//iframe[1]')))
            iframe = driver.find_elements(By.XPATH, '//iframe')[1]
            driver.execute_script("arguments[0].click();", iframe)
            time.sleep(3)
            driver.switch_to.frame(iframe)
            time.sleep(1)
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//video')))
            video = driver.find_element(By.XPATH, '//video').get_attribute('src')

            file_extension = video.split('.')[-1]

            # check movie or series
            checker = video.split('/')[-1].split('.')[0]
            if 'x' not in checker:
                return video, f'.{file_extension}'

            print('Detected as a series, finding which episode of which season to download')

            # check max series
            season = 1
            while True:
                temp = f'{season}x01'
                link = video.replace(checker, temp)
                response = requests.head(link, verify=False, headers=get_request_headers())
                if 'checkcaptcha' in driver.current_url:
                    handle_captcha(driver)
                    continue
                if response.status_code != 200:
                    break
                time.sleep(1)
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
                if 'checkcaptcha' in driver.current_url:
                    handle_captcha(driver)
                    continue
                if response.status_code != 200:
                    break
                time.sleep(1)
                episode += 1

            valid_episode = episode - 1
            if valid_episode <= 9:
                valid_episode = f'0{valid_episode}'
            return video.replace(checker,
                                 f'{valid_season}x{valid_episode}'), f'{valid_season}x{valid_episode}.{file_extension}'
        except Exception as e:
            print(e)
            print(f'Failed to generate video download link, retrying #{i + 1}')
            time.sleep(5)
            continue
    return None, None


def run():
    print('===============================================================')
    print('Script starts running. Don not close the automated browser ...')
    csv_init()
    driver = config_driver()
    break_pointer = get_break_pointer(driver, 'https://tainio-mania.online')
    print(f'Content will be downloaded next to this `{break_pointer}`')
    while True:
        try:
            downloadable_items = reverse_list(get_detail_page_links(driver, break_pointer))
            if len(downloadable_items) < 1:
                print('No new content available to download, waiting for next try..')
                time.sleep(300)
                continue

            for content in downloadable_items:
                print(f'Fetch video download link for -> {content["title"]}')

                link, name = get_video_link(driver, content['link'])
                if link is None:
                    print(f'`{content["title"]}` -> Failed to generate downloadable link, moving next..')
                    continue

                for i in range(3):
                    try:
                        download_manager(f'{str(content["title"]).replace("/", "|")}_{name}', link)
                        print('Successfully downloaded!')
                        break
                    except Exception as e:
                        print(f'`{content["title"]}` -> Failed to download this content, retrying..')
                        continue

            break_pointer = downloadable_items[0]['title']
        except Exception as e:
            print('Website is not responding, retrying ...')
            time.sleep(10)


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_FOLDER_PATH):
        print('Invalid output folder path')
    else:
        run()
