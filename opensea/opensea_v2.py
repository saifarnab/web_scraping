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
subprocess.check_call(['pip', 'install', 'pillow'])
subprocess.check_call(['pip', 'install', 'requests'])
subprocess.check_call(['pip', 'install', 'openpyxl'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'fake_useragent'])


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


def scrapper():
    print('-------------------------------------------------------------')
    print('-------------------------------------------------------------')
    print('Script starts running... ')
    filename = 'opensea.xlsx'
    create_directory_if_not_exists('images')
    create_excel_with_header(filename)
    azuki = get_last_row(filename) - 1
    print('Starting data extraction ... ')
    reloader = 1
    while True:
        if azuki >= 10000:
            break
        driver = config_driver()
        driver.get(f'https://opensea.io/assets/ethereum/0xed5af388653567af2f388e6224dc7c4b3241c544/{azuki}')

        if reloader >= 10:
            azuki += 1

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//img[@class="Image--image"]')))
        except Exception as e:
            # print('Retrying without fake user-agent chrome driver')
            driver = config_driver_without_ua()
            driver.get(f'https://opensea.io/assets/ethereum/0xed5af388653567af2f388e6224dc7c4b3241c544/{azuki}')
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//img[@class="Image--image"]')))
            except Exception as ex:
                # print('Retrying with fake user-agent chrome driver')
                reloader += 1
                continue

        name = f'Azuki #{azuki}'
        link = driver.current_url
        src = driver.find_element(By.XPATH, '//img[@class="Image--image"]').get_attribute('src')
        if check_data_exists(filename, name) is False:
            if save_as_jpg(src, name) is True:
                append_to_excel(filename, [[azuki, link, name, f'{name}.jpg']])
                print(f'--> {azuki}. {name} inserted')
        else:
            print(f'--> {name} is already available.')

        azuki += 1
        reloader = 1

    print('Execution done!')


if __name__ == '__main__':
    scrapper()
