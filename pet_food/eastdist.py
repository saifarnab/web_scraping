import os
import subprocess
import time
from io import BytesIO

import openpyxl
import pandas as pd
import requests
from PIL import Image
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def create_excel_with_header():
    filename= 'eastdist.xlsx'
    if os.path.exists(filename) is True:
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['TITLE', 'SKU', 'APN', 'BRAND', 'WEIGHT', 'PRICE', 'LINK'])
    workbook.save(filename)


def create_product_csv():
    df = pd.DataFrame(columns=["Link"])
    df.to_csv('eastdist_link.csv', index=False)
    print('eastdist_link file have been created')


def insert_product_links(links: list):
    existing_data = pd.read_csv('eastdist_link.csv')
    new_data = pd.DataFrame({'Link': links})
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv('eastdist_link.csv', index=False)


def login(driver: webdriver.Chrome):
    driver.get('https://pronto.eastdist.com/login')
    driver.find_element(By.ID, 'user_email_address').send_keys('andrew@smartwaypetsupplies.com.au')
    driver.find_element(By.ID, 'user_password').send_keys('Smartway@82')
    driver.find_element(By.XPATH, "//button[@class='btn btn-primary radius-10 signin-btn']").click()


def extract_data(driver: webdriver.Chrome):
    for product_page in range(587):
        driver.get(f'https://pronto.eastdist.com/search?product_page={product_page + 1}')
        product_details_links = []
        product_details_link_elms = driver.find_elements(By.XPATH, '//a[@class="av-result-title"]')
        for product_details_link_elm in product_details_link_elms:
            product_details_links.append(product_details_link_elm.get_attribute('href'))

        insert_product_links(product_details_links)
        print(f'{len(product_details_links)} products have been inserted!s')


def ends_with_any(text):
    word_list = ['G', 'ML', 'L', 'KG', 'LT']
    for word in word_list:
        if text.endswith(word):
            return True
    return False


def insert_data_into_excel(data):
    df = pd.read_excel("eastdist.xlsx")
    new_data = pd.DataFrame(data, columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("eastdist.xlsx", index=False)
    print(f"{data[0]} has been inserted into the output file")


def extract_product_data(driver: webdriver.Chrome):
    df = pd.read_csv('eastdist_link.csv')
    products = df['Link'].values
    for product_link in products:
        driver.get(product_link)
        try:
            title = driver.find_element(By.XPATH, '//h2[@class=" av-product-title section-title mt-0"]').text
        except:
            title = ''

        try:
            item_code = driver.find_element(By.XPATH, '//div[@class="item-code"]').text
        except:
            item_code = ''

        try:
            price = driver.find_element(By.XPATH, '//span[@class="price"]').text
        except:
            price = ''

        try:
            brand_name = driver.find_element(By.XPATH, '//tbody/tr[2]/td[2]"').text
        except:
            brand_name = ''

        if title != '' and ends_with_any(title) is True:
            weight = title.split()[-1]
        else:
            weight = ''

        insert_data_into_excel([[title, item_code, '', brand_name, weight, price, product_link]])
        print(f'{title} -> inserted!')


def run():
    # create_product_csv()
    create_excel_with_header()
    driver = config_driver()
    login(driver)
    extract_product_data(driver)


if __name__ == '__main__':
    run()
