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
    df.to_csv('petstock_product.csv', index=False)
    print('petstock product file have been created')


def insert_products(product_url: list):
    existing_data = pd.read_csv('petstock_product.csv')
    new_data = pd.DataFrame({'url': product_url})
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv('petstock_product.csv', index=False)


def create_excel_with_header():
    filename = 'petstock.xlsx'
    if os.path.exists(filename) is True:
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['Link', 'ProductName', 'Price'])
    workbook.save(filename)


def insert_data_into_excel(data):
    df = pd.read_excel("petstock.xlsx")
    new_data = pd.DataFrame(data, columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("petstock.xlsx", index=False)


def get_products(driver: webdriver.Chrome):
    # ?page=1&resultsPerPage=16&view=products
    # urls = [
    #     'https://www.petstock.com.au/collections/dog'
    #     'https://www.petstock.com.au/collections/cat',
    #     'https://www.petstock.com.au/collections/fish',
    #     'https://www.petstock.com.au/collections/horse',
    #     'https://www.petstock.com.au/collections/bird',
    #     'https://www.petstock.com.au/collections/small-animal',
    #     'https://www.petstock.com.au/collections/reptile',
    # ]

    # for i in range(1, 10):
    #     url = f'https://www.petstock.com.au/collections/reptile?page={i}&resultsPerPage=25&view=products'
    #     insert_products([url])

    df = pd.read_csv('petstock_product.csv')
    df = df['url'].values

    for ind, url in enumerate(df):
        driver.get(url)
        time.sleep(7)

        cart_xpath = '//div[@class="product-card-contentstyled__ProductCardContainer-sc-12pzt0r-0 gqVWEj"]'
        carts = driver.find_elements(By.XPATH, cart_xpath)
        for item in carts:
            try:
                link = item.find_element(By.XPATH,
                                         './/a[@class="product-card-contentstyled__Title-sc-12pzt0r-3 jeIAfn"]').get_attribute(
                    'href')
            except:
                link = ''

            try:
                title = item.find_element(By.XPATH,
                                          './/a[@class="product-card-contentstyled__Title-sc-12pzt0r-3 jeIAfn"]').text

            except:
                title = ''

            try:
                price = item.find_element(By.XPATH,
                                          './/div[@class="product-card-pricesstyled__PriceGroup-sc-1eylvho-5 jTTaAv"]').text.replace(
                    '\n', '')

            except:
                price = ''

            insert_data_into_excel([[link, title, price]])

        print(f'{ind + 1}. Insert {len(carts)} data from -> {url}')


def run():
    # create_excel_with_header()
    driver = config_driver()
    get_products(driver)


if __name__ == '__main__':
    run()
