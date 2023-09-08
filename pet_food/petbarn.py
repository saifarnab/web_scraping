import os
import time

import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def create_product_csv():
    df = pd.DataFrame(columns=["url"])
    df.to_csv('petbarn_product.csv', index=False)
    print('petbarn product file have been created')


def insert_products(product_url: list):
    existing_data = pd.read_csv('petbarn_product.csv')
    new_data = pd.DataFrame({'url': product_url})
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv('petbarn_product.csv', index=False)


def create_excel_with_header():
    filename = 'petbarn.xlsx'
    if os.path.exists(filename) is True:
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Link', 'ProductName', 'Price'])
    workbook.save(filename)


def insert_data_into_excel(data):
    df = pd.read_excel("petbarn.xlsx")
    new_data = pd.DataFrame(data, columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("petbarn.xlsx", index=False)


def get_products(driver: webdriver.Chrome):
    urls = [
        {
            'url': 'https://www.petbarn.com.au/dogs?p=',
            'max': 175
        },
        {
            'url': 'https://www.petbarn.com.au/cats?p=',
            'max': 77
        },
        {
            'url': 'https://www.petbarn.com.au/small-animal/?p=',
            'max': 11
        },
        {
            'url': 'https://www.petbarn.com.au/fish/?p=',
            'max': 32
        },
        {
            'url': 'https://www.petbarn.com.au/bird/?p=',
            'max': 17
        },
        {
            'url': 'https://www.petbarn.com.au/reptile/?p=',
            'max': 11
        },
        {
            'url': 'https://www.petbarn.com.au/chicken/?p=',
            'max': 4
        },
    ]

    for item in urls:
        for i in range(1, item['max'] + 1):
            driver.get(f'{item["url"]}{i}')
            time.sleep(7)
            carts = driver.find_elements(By.XPATH, '//div[@class="product-item-info"]')
            for cart in carts:
                try:
                    link = cart.find_element(By.XPATH, './/a[@class="product-item-link"]').get_attribute('href')
                except:
                    link = ''
                try:
                    title = cart.find_element(By.XPATH, './/a[@class="product-item-link"]').text
                except:
                    title = ''
                try:
                    price = cart.find_element(By.XPATH, './/span[@class="price-wrapper  "]').text
                except:
                    try:
                        price = cart.find_element(By.XPATH, './/div[@class="price-box member-price"]').text
                    except:
                        price = ''
                insert_data_into_excel([[link, title, price]])

            print(f'{len(carts)} products inserted for {item["url"]}{i}')

def run():
    create_excel_with_header()
    driver = config_driver()
    get_products(driver)


if __name__ == '__main__':
    run()
