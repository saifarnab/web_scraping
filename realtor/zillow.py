import sys
import time
from os.path import exists
import csv
from pandas import read_csv
from user_agent import generate_user_agent
import datetime
import subprocess

import requests
from bs4 import BeautifulSoup
from lxml import etree
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# install dependencies
# subprocess.check_call(['pip', 'install', 'bs4'])
# subprocess.check_call(['pip', 'install', 'requests'])
# subprocess.check_call(['pip', 'install', 'lxml'])

def config_driver():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    # user_agent = generate_user_agent()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def config_uc_driver():
    user_agent = generate_user_agent()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = uc.Chrome(options=chrome_options)
    return driver


def csv_file_init(file_name: str):
    try:
        with open(file_name, 'x', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                ["DateTime", "Category", "Property Type", "Address", "Bedrooms", "Bathrooms", "Price", "Link",
                 "Telephone", "Managed", "Pool", "Furnished", "zillow Link", "zillow Number"])
            print('File created successfully.')
    except FileExistsError:
        pass


def write_csv(file_name: str, new_row: list) -> bool:
    flag = True
    add_hyperlink = f'=HYPERLINK("{new_row[12]}","{new_row[12]}")'
    new_row[6] = add_hyperlink
    with open(file_name, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if line and new_row[12].strip() == line[12].strip():
                flag = False
                break

    if flag is False:
        print('This property already available ignoring..')
        return False

    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)

    return True


def get_address(filename: str) -> list:
    try:
        print(filename)
        data = read_csv(filename)
        return data['Address'].tolist()
    except Exception as e:
        print('Address column not found in csv, exiting')
        exit()


def close_program(msg: str):
    print(msg)
    print('Script successfully executed!')
    exit()


def scrapper(filename: str):
    print('---------------------------******----------------------')
    print('Script starts ...')

    zillow_filename = f'zillow_{filename}'
    csv_file_init(zillow_filename)
    addresses = get_address(filename)

    address_pointer = 0
    while address_pointer < len(addresses):
        address = addresses[address_pointer]
        driver = config_driver()
        driver.get(f'https://www.zillow.com/homes/{address}')
        time.sleep(1)
        print(driver.current_url)
        zillow_url, telephone = '', ''
        if 'captchaPerimeterX' in driver.current_url:
            print('captcha issue generated')
            address_pointer += 1
            driver.find_element(By.XPATH, "//div[@id='px-captcha']")
            time.sleep(10000)

        elif '/b/' in driver.current_url:
            try:
                zillow_url = driver.current_url
                WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//span[@class="RCFAgentPhoneDesktopText__phoneNumber"]')))

                telephone = driver.find_element(By.XPATH, '//span[@class="RCFAgentPhoneDesktopText__phoneNumber"]').text
            except Exception as e:
                telephone = ''

        address_pointer += 1
        print(zillow_url, telephone)
        driver.close()
        time.sleep(1)


if __name__ == "__main__":
    try:
        file = sys.argv[1]
        if exists(file) is False:
            print(f'{file} not available')
        else:
            scrapper(file)
    except Exception as e:
        print(e)
        print('No filename define')
