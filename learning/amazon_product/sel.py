import os
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pandas as pd
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    driver = webdriver.Chrome()
    if maximize_window is True:
        driver.maximize_window()
    return driver

    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_argument('--disable-browser-side-navigation')
    # options.add_argument("--enable-javascript")
    # if maximize_window is True:
    #     options.add_argument("--headless")
    # driver = webdriver.Chrome(options=options)
    # if maximize_window is False:
    #     driver.maximize_window()
    # return driver


def get_input() -> str:
    print('Enter the product name you want to search: ')
    searchable_product = str(input('> '))
    print('Start storing data...')
    return searchable_product


def get_products():
    website = 'https://www.amazon.in/'
    searchable_product = get_input()

    # define 'driver' variable
    driver = config_driver(False)
    driver.get(website)

    # search by product name
    search = driver.find_element(By.ID, 'twotabsearchtextbox')
    search.send_keys(searchable_product)
    search.send_keys(Keys.RETURN)
    time.sleep(2)

    # get total pagination
    pages = int(driver.find_element(By.XPATH, "//span[@class='s-pagination-item s-pagination-disabled']").text.strip())

    # get products
    # list of columns
    products = []
    for i in range(1, pages):
        products = driver.find_elements(By.XPATH, "//div[@class='a-section a-spacing-small a-spacing-top-small']")
        for ind, product in enumerate(products):
            try:
                if ind == 0:
                    continue

                windows_before = driver.window_handles
                product_name = product.find_element(By.XPATH, "./div[1]/h2/a/span").text
                product_link = product.find_element(By.XPATH, "./div[1]/h2/a")

                # go to product details page
                product_link.click()
                WebDriverWait(driver, 10).until(EC.new_window_is_opened(windows_before))
                driver.switch_to.window([x for x in driver.window_handles if x not in windows_before][0])

                # click to `see more` to expand description
                try:
                    see_more = driver.find_element(By.XPATH, "//div[@id='poToggleButton']/a/span")
                    see_more.click()
                except Exception as ex:
                    pass

                # extract description
                product_description_table = driver.find_elements(By.XPATH,
                                                                 "//div[@id ='poExpander']/div[1]/div[1]/table/tbody/tr")
                product_description = ""
                for each_item in product_description_table:
                    if each_item.find_element(By.XPATH, './td[1]/span').text != "":
                        product_description += f"{each_item.find_element(By.XPATH, './td[1]/span').text}: {each_item.find_element(By.XPATH, './td[2]/span').text}, "

                # extract product img
                pim1, pim2, pim3, pim4, pim5 = '', '', '', '', ''
                for img_ind, img in enumerate(driver.find_elements(By.CSS_SELECTOR, '#altImages .imageThumbnail')):
                    hover = ActionChains(driver).move_to_element(img)
                    hover.perform()
                    img_url = driver.find_element(By.CSS_SELECTOR,
                                                  '.image.item.maintain-height.selected img').get_attribute(
                        'src').strip()
                    img_extension = img_url.split('.')[-1]
                    with open(f"{Path().absolute().__str__()}/amazon_product_scraping/data/images/{product_name}_{img_ind + 1}.{img_extension}",
                              "wb") as f:
                        f.write(requests.get(img_url).content)
                        if img_ind + 1 == 1:
                            pim1 = f"{product_name}_{img_ind + 1}.{img_extension}"
                        if img_ind + 1 == 2:
                            pim2 = f"{product_name}_{img_ind + 1}.{img_extension}"
                        if img_ind + 1 == 3:
                            pim3 = f"{product_name}_{img_ind + 1}.{img_extension}"
                        if img_ind + 1 == 4:
                            pim4 = f"{product_name}_{img_ind + 1}.{img_extension}"
                        if img_ind + 1 == 5:
                            pim5 = f"{product_name}_{img_ind + 1}.{img_extension}"

                    if img_ind >= 4:
                        break

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                product_price = product.find_element(By.XPATH,
                                                     "./div[3]/div[1]/div[1]/div[1]/div[1]/a/span").text.strip()
                if product_price == 'Limited time deal':
                    product_price = product.find_element(By.XPATH,
                                                         "./div[3]/div[1]/div[1]/div[1]/div[2]/a/span").text.strip()

                product = [product_name.strip(), product_link.get_attribute('href').strip(), product_price, pim1, pim2,
                           pim3, pim4, pim5]
                products.append(product)
            except Exception as ex:
                pass

        next_page = driver.find_element(By.XPATH,
                                        "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
        next_page.click()
        time.sleep(1)

    make_xls(products, searchable_product)
    driver.quit()


def make_xls(products: list, searchable_product: str):
    df = pd.DataFrame(products, columns=["title", "url", "price", "img1", "img2", "img3", "img4", "img5"])
    df.to_excel(f"data/{searchable_product}.xlsx", index=False)


if __name__ == '__main__':
    get_products()
