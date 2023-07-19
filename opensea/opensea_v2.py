import os
import subprocess
from io import BytesIO

import openpyxl
import requests
from PIL import Image
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# install dependencies
# subprocess.check_call(['pip', 'install', 'pillow'])
# subprocess.check_call(['pip', 'install', 'requests'])
# subprocess.check_call(['pip', 'install', 'openpyxl'])
# subprocess.check_call(['pip', 'install', 'selenium'])
# subprocess.check_call(['pip', 'install', 'fake_useragent'])


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def config_driver_without_ua() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exist.")


def save_as_jpg(src: str, name: str):
    reloader = 1
    while True:
        if reloader >= 10:
            return False
        response = requests.get(src)
        if response.status_code == 200:
            im = Image.open(BytesIO(response.content))
            rgb_im = im.convert('RGB')
            rgb_im.save(f'images/{name}.jpg')
            return True
        reloader += 1


def append_to_excel(filename, data):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in data:
        sheet.append(row)
    workbook.save(filename)


def create_excel_with_header(filename):
    if os.path.exists(filename) is True:
        print(f'{filename} already exist')
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['No.', 'Link', 'Name', 'Image Name'])
    workbook.save(filename)
    print(f'{filename.title()} created')


def get_last_row(filename):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    last_row = sheet.max_row
    return last_row


def check_data_exists(filename: str, name: str) -> bool:
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in sheet.iter_rows(values_only=True):
        if name.strip() == row[2].strip():
            return True  # Data exists in the sheet
    return False  # Data does not exist in the sheet


def is_access_denied(driver) -> bool:
    try:
        driver.find_element(By.XPATH, '//div[@class="cf-error-title"]')
        return True
    except Exception as e:
        return False


def _take_input_url() -> str:
    return input('Enter a sample detail url: ')


def _generate_base_url(url: str) -> str:
    base_url = url.rsplit('/', 1)[0]
    return base_url


def scrapper():
    print('-------------------------------------------------------------')
    print('-------------------------------------------------------------')
    print('Script starts running... ')
    url = _take_input_url()
    base_url = _generate_base_url(url)
    init, reloader, nft, name, filename = 0, 1, 0, '', ''
    print('Starting data extraction ... ')
    while True:

        if init == 0:
            try:
                driver = config_driver()
                driver.get(url)
                try:
                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'item--header')))
                except Exception as e:
                    continue

                name = driver.find_element(By.TAG_NAME, 'h1').text.split('#')[0].strip()
                create_directory_if_not_exists(f'images/{name}')
                create_directory_if_not_exists('files')
                filename = f'files/{name}.xlsx'
                create_excel_with_header(filename)
                nft = get_last_row(filename) - 1
            except:
                try:
                    driver = config_driver_without_ua()
                    driver.get(url)
                    name = driver.find_element(By.TAG_NAME, 'h1').text.split('#')[0].strip()
                    create_directory_if_not_exists(f'images/{name}')
                    create_directory_if_not_exists('files')
                    filename = f'files/{name}.xlsx'
                    nft = get_last_row(filename) - 1
                except:
                    continue
            init = 1

        else:
            if nft >= 10000:
                break
            driver = config_driver()
            driver.get(f'{base_url}/{nft}')

            if reloader >= 10:
                nft += 1

            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//img[@class="Image--image"]')))
            except Exception as e:
                # print('Retrying without fake user-agent chrome driver')
                driver = config_driver_without_ua()
                driver.get(f'{base_url}/{nft}')
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, '//img[@class="Image--image"]')))
                except Exception as ex:
                    # print('Retrying with fake user-agent chrome driver')
                    reloader += 1
                    continue

            link = driver.current_url
            src = driver.find_element(By.XPATH, '//img[@class="Image--image"]').get_attribute('src')
            temp_name = f'{name} #{nft}'
            if check_data_exists(filename, temp_name) is False:
                if save_as_jpg(src, f'{name}/{temp_name}') is True:
                    append_to_excel(filename, [[nft, link, temp_name, f'{temp_name}.jpg']])
                    print(f'--> {nft}. {temp_name} inserted')
            else:
                print(f'--> {temp_name} is already available.')

            nft += 1
            reloader = 1

    print('Execution done!')


if __name__ == '__main__':
    scrapper()
