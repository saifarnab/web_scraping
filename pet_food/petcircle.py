import os
import time

import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def create_excel_with_header():
    filename = 'petcircle.xlsx'
    if os.path.exists(filename) is True:
        return
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(['TITLE', 'descriptions', 'prices', 'Image1', 'Image2', 'Image3', 'Image4', 'Image5', 'Image6', 'Link'])
    workbook.save(filename)


def create_brand_url_csv():
    df = pd.DataFrame(columns=["brand"])
    df.to_csv('petcircle_brand.csv', index=False)
    print('petcircle_brand file have been created')


def create_product_url_csv():
    df = pd.DataFrame(columns=["product_url"])
    df.to_csv('petcircle_product_url.csv', index=False)
    print('petcircle_product_url file have been created')


def insert_brands(brands_url: list):
    existing_data = pd.read_csv('petcircle_brand.csv')
    new_data = pd.DataFrame({'brand': brands_url})
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv('petcircle_brand.csv', index=False)


def insert_products(products_url: list):
    existing_data = pd.read_csv('petcircle_product_url.csv')
    new_data = pd.DataFrame({'product_url': products_url})
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    combined_data.to_csv('petcircle_product_url.csv', index=False)


def insert_data_into_excel(data):
    df = pd.read_excel("petcircle.xlsx")
    new_data = pd.DataFrame(data, columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("petcircle.xlsx", index=False)


def get_brand_urls(driver: webdriver.Chrome):
    driver.get('https://www.petcircle.com.au/brand')
    links = driver.find_elements(By.XPATH, '//span[@class="link-wrapper"]/a')
    for link in links:
        insert_brands([link.get_attribute('href')])


def get_product_urls(driver: webdriver.Chrome):
    df = pd.read_csv('petcircle_brand.csv')
    brands = df['brand'].values
    for brand in brands:
        page = 1
        while True:
            driver.get(f'{brand}?page={page}')
            # driver.get(f'https://www.petcircle.com.au/chuckit?page={page}')
            time.sleep(5)
            products1 = driver.find_elements(By.XPATH, '//div[@class="product-box-image "]/a')
            for product in products1:
                insert_products([product.get_attribute('href')])

            products2 = driver.find_elements(By.XPATH, '//div[@class="product-box-image sale"]/a')
            for product in products2:
                insert_products([product.get_attribute('href')])
            products3 = driver.find_elements(By.XPATH, '//div[@class="product-box-image soldout"]/a')
            for product in products3:
                insert_products([product.get_attribute('href')])
            total = len(products1) + len(products2) + len(products3)
            print(f'{driver.current_url} inserted total products = {total}')
            if total < 35:
                break
            page += 1


def get_products(driver: webdriver.Chrome):
    df = pd.read_csv('petcircle_product_url.csv')
    product_urls = df['product_url'].values
    for ind, product_url in enumerate(product_urls):
        driver.get(product_url)
        time.sleep(2)
        try:
            title = driver.find_element(By.XPATH, "//span[@id='brandlessDisplayName']//span").text
        except:
            title = ''
        try:
            des = driver.find_element(By.XPATH, '//div[@id="about-content-mob"]').text
        except:
            des = ''
        try:
            price = driver.find_element(By.XPATH, '//span[@data-testid="once-off-price"]').text
        except:
            price = ''
        img1, img2, img3, img4, img5, img6 = '', '', '', '', '', ''
        try:
            imgs = driver.find_elements(By.XPATH, '//img[@class="swiper-lazy swiper-lazy-loaded"]')

            if len(imgs) > 2:
                img = imgs[0].get_attribute('src').replace('.png', '')
                for i in range(len(imgs)):
                    if i + 1 == 1:
                        img1 = f'{img}___{i + 1}.png'
                    elif i + 1 == 2:
                        img2 = f'{img}___{i + 1}.png'
                    elif i + 1 == 3:
                        img3 = f'{img}___{i + 1}.png'
                    elif i + 1 == 4:
                        img4 = f'{img}___{i + 1}.png'
                    elif i + 1 == 5:
                        img5 = f'{img}___{i + 1}.png'
                    elif i + 1 == 6:
                        img6 = f'{img}___{i + 1}.png'
            else:
                img1 = imgs[0].get_attribute('src')
        except:
            pass

        insert_data_into_excel([[title, des, price, img1, img2, img3, img4, img5, img6, driver.current_url]])
        print(f'{ind+1}. {title} inserted')
        time.sleep(1)


def run():
    # create_brand_url_csv()
    # create_product_url_csv()
    # create_excel_with_header()
    driver = config_driver()
    get_products(driver)


if __name__ == '__main__':
    run()
