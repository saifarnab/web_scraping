import os

import openpyxl
import requests
from PIL import Image
from io import BytesIO

import pillow_avif
import csv
import datetime
import subprocess
import time

import pandas as pd
from pandas import ExcelWriter
from selenium.webdriver import Keys

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


def config_driver() -> webdriver.Firefox:
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--lang=en_US")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 1})
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    # chrome_options.add_argument("javascript.enabled")
    chrome_options.add_argument("disable-infobars")
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--window-size=1920,1080")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    chrome_options.add_argument('user-agent={0}'.format(user_agent))
    driver = webdriver.Firefox(options=chrome_options)
    return driver


def scroll_down_page(driver):
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
    # driver.execute_script(f"window.scrollTo(0, 210);")
    # html = driver.find_element(By.TAG_NAME, 'html')
    # for i in range(0, 20):
    #     html.send_keys(Keys.ARROW_DOWN)


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")


def convert_avif_to_png(src: str, name: str):
    response = requests.get(src)
    im = Image.open(BytesIO(response.content))
    rgb_im = im.convert('RGB')
    rgb_im.save(f'images/{name}.jpg')


def append_to_excel(filename, data):
    # Load the existing workbook
    workbook = openpyxl.load_workbook(filename)

    # Select the active sheet or a specific sheet by name
    sheet = workbook.active
    # sheet = workbook['Sheet1']  # Replace 'Sheet1' with the actual sheet name

    # Append the new data to the sheet
    for row in data:
        sheet.append(row)

    # Save the modified workbook
    workbook.save(filename)


def create_excel_with_header(filename):
    if os.path.exists(filename) is True:
        return
    # Create a new workbook and select the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Write the headers to the sheet
    sheet.append(['No.', 'Link', 'Name', 'Image Name'])

    # Save the workbook
    workbook.save(filename)
    print(f'{filename} created')


def get_last_row(filename):
    # Load the workbook
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active

    # Get the maximum row number with data in the selected sheet
    last_row = sheet.max_row

    return last_row


def check_data_exists(filename: str, name: str) -> bool:
    # Load the workbook
    workbook = openpyxl.load_workbook(filename)

    # Select the desired sheet
    sheet = workbook.active

    # Iterate through the rows in the sheet
    for row in sheet.iter_rows(values_only=True):
        # Compare each cell value to the desired data
        if name.strip() == row[2].strip():
            return True  # Data exists in the sheet

    return False  # Data does not exist in the sheet


def scrapper():
    print('Script starts running... ')
    filename = 'opensea.xlsx'
    create_directory_if_not_exists('images')
    create_excel_with_header(filename)
    driver = config_driver()
    driver.get('https://opensea.io/collection/azuki')
    time.sleep(5)
    no = get_last_row(filename)
    breaker = 0
    pre = 0
    post = 3000
    while True:
        pre_height = driver.execute_script("return document.documentElement.scrollHeight")
        scroll_down_page(driver, pre, post)
        pre = post
        post += 500
        articles = driver.find_elements(By.XPATH,
                                        '//div[@class="sc-29427738-0 sc-7ac0e573-1 cKdnBO iCfZHJ Asset--loaded"]')

        for article in articles:
            link = driver.find_element(By.XPATH, './/article/a').get_attribute('href')
            img = article.find_element(By.XPATH, './/img')
            src = img.get_attribute('src')
            name = img.get_attribute('alt')
            if 'https' in src:
                if check_data_exists(filename, name) is False:
                    convert_avif_to_png(src, name)
                    append_to_excel(filename, [[no, link, name, f'{name}.jpg']])
                    print(f'--> {no}. {name} inserted')
                    no += 1
                else:
                    print('nil')

        post_height = driver.execute_script("return document.documentElement.scrollHeight")
        if pre_height == post_height:
            breaker += 1
            time.sleep(2)
        else:
            breaker = 0

        if breaker >= 10:
            break

    print('Execution done!')


if __name__ == '__main__':
    # scrapper()

    driver = config_driver()
    driver.get('https://opensea.io/collection/azuki')
    time.sleep(1000)
    # scroll_down_page(driver)