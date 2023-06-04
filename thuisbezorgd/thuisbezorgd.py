import csv
import logging
import math
import random
import subprocess
import sys
import time

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By

# install dependencies
subprocess.check_call(['pip', 'install', 'undetected-chromedriver'])
subprocess.check_call(['pip', 'install', 'selenium'])

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


# chrome driver configuration
def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-miniimized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = uc.Chrome(options=chrome_options)
    return driver


# wait until an element is ready from DOM
def wait_until_find_element(driver, selector, param):
    start_time = time.time()
    while True:
        try:
            driver.find_element(selector, param)
            break
        except Exception as e:
            if math.ceil(time.time() - start_time) > 15:
                break
            continue


# close cookies pop up
def handle_cookies_popup(driver):
    try:
        cookies_ok_button = driver.find_element(By.XPATH, "//button[@class='_908LZ _1bx49 _20B3B _4R7G3 YG2eu _2JFg2']")
        cookies_ok_button.click()
        logging.info('handling cookies pop up ...')
    except Exception as e:
        pass


# method for scrolling the page
def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# check valid postcode
def postcode_validation(driver, postcode) -> bool:
    if "redirected" in driver.current_url:
        logging.info(f'no data.bson available for `{postcode}` postcode')
        return False
    return True


def scanner(driver, postcode, store, f_name):
    parent = driver.window_handles[0]
    logging.info(f'start loading url for <{postcode}> postcode')
    driver.get('https://www.thuisbezorgd.nl/bestellen/eten/amsterdam-' + postcode)
    time.sleep(3)
    if postcode_validation(driver, postcode) is False:
        return []

    wait_until_find_element(driver, By.XPATH, '//h1[@data.bson-qa="restaurant-list-header"]')
    handle_cookies_popup(driver)

    # load the page completely by scrolling bottom
    start_time = time.time()
    logging.info('--> rendering places ...')
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(parent)
    scroll_down(driver)
    driver.execute_script("window.scrollTo(0, 0);")
    logging.info(f"{math.ceil(time.time() - start_time)}s to render all the places")
    time.sleep(1)

    # iterate each restaurant
    wait_until_find_element(driver, By.XPATH, '//a[@class="_9NUh1 qT7x_"]')
    restaurants = driver.find_elements(By.XPATH, '//a[@class="_9NUh1 qT7x_"]')
    logging.info(f"{len(restaurants)} places found for {postcode} location key")

    # get child tab
    child = driver.window_handles[1]
    for ind, item in enumerate(restaurants):

        try:
            start_time = time.time()
            # extract name, rating, reviews & details page link
            name = item.find_element(By.XPATH, './/h3[@data.bson-qa="restaurant-info-name"]').text
            details_page_link = item.get_attribute('href')

            # Open a new window & Switch to the new window
            driver.switch_to.window(child)
            # time.sleep(1)
            driver.get(details_page_link)
            time.sleep(2)

            # read & concat all available categories
            categories_str = ''
            try:
                wait_until_find_element(driver, By.XPATH, '//div[@class="_3wa4B"]')
                categories = driver.find_elements(By.XPATH, '//div[@class="_3wa4B"]')
                for categories_ind, categories_item in enumerate(categories):
                    if categories_ind == 0:
                        continue
                    if categories_item.text != "":
                        categories_str += f"{categories_item.text}, "
            except Exception as e:
                pass

            # click to i button
            try:
                i_button = driver.find_element(By.XPATH, '//span[@data.bson-qa="restaurant-header-action-info"]')
                i_button.click()
                time.sleep(2)
            except Exception as e:
                pass

            try:
                driver.find_element(By.XPATH, '//h1[@class="_50YZr _2A4nS"]')
                address_str = ''
                opening_time_str = ''
                rating = ''
                logging.info(
                    f"---> failed to load `i` button. getting 500.")

            except Exception as ex:

                # extract address
                address_str = ''
                try:
                    wait_until_find_element(driver, By.XPATH, '//div[@data.bson-qa="restaurant-info-modal-header"]')
                    wait_until_find_element(driver, By.XPATH,
                                            '//div[@data.bson-qa="restaurant-info-modal-info-address-element"]//div['
                                            '@data.bson-qa="text"]')
                    addresses = driver.find_elements(By.XPATH,
                                                     '//div[@data.bson-qa="restaurant-info-modal-info-address-element"]//div['
                                                     '@data.bson-qa="text"]')

                    for addr in addresses:
                        if addr.text != '':
                            address_str += f"{addr.text}, "
                except Exception as e:
                    pass

                # extract opening time
                opening_time_str = ''
                try:
                    wait_until_find_element(driver, By.XPATH,
                                            '//div[@data.bson-qa="restaurant-info-modal-info-shipping-times-element-element'
                                            '"]//div[@class="_1sMed _1wlHd _2cDMI"]')
                    opening_times = driver.find_elements(By.XPATH,
                                                         '//div[@data.bson-qa="restaurant-info-modal-info-shipping-times'
                                                         '-element-element"]//div[@class="_1sMed _1wlHd _2cDMI"]')

                    for opening_time_ind, opening_time_item in enumerate(opening_times):
                        elements = opening_time_item.find_elements(By.XPATH, './/div[@data.bson-qa="text"]')
                        opening_time_str += f"{elements[0].text}: {elements[1].text}"
                        opening_time_str += '\n'
                except Exception as e:
                    pass

                # extracting rating & review
                try:
                    rating_button = driver.find_element(By.XPATH, '//button[@id="restaurant-about-tab-reviews"]')
                    rating_button.click()
                    time.sleep(1)
                    rating = driver.find_element(By.XPATH,
                                                 '//div[@data.bson-qa="restaurant-info-modal-reviews-rating"]//div[@class="_50YZr _3-Fnx"]').text
                    review = driver.find_element(By.XPATH, '//div[@class="_2oup6D"]//div[@class="Tcels"][1]').text.replace('\n', '')
                    rating = f"{rating.strip()}{review.strip()}"
                    if rating[0:3] == rating[3:6]:
                        rating = rating[3:]
                    if rating[1] != ',':
                        rating = rating[0] + ',' + rating[1:]
                    rating = rating[0:3] + ", " + rating[3:]
                except Exception as ex:
                    print(ex)
                    rating = ''

            # extracting delivery time
            try:
                delivery_time = driver.find_element(By.XPATH, '//div[@data.bson-qa="shipping-time-indicator-content"]').text
            except Exception as e:
                delivery_time = ''

            # extracting delivery cost
            try:
                delivery_cost = driver.find_element(
                    By.XPATH, '//div[@data.bson-qa="delivery-costs-indicator"]//span[@class="_2PRj3E"]').text
            except Exception as e:
                delivery_cost = ''

            # extracting minimum order
            try:
                minimum_order = driver.find_element(
                    By.XPATH, '//div[@data.bson-qa="mov-indicator-content"]//span[@class="_2PRj3E"]').text
            except Exception as e:
                minimum_order = ''

            logging.info(
                f"---> {ind + 1}. <{name}> restaurant's data.bson is extracted!- required time <{math.ceil(time.time() - start_time)}s>")

            temp_data = [postcode, name, address_str, opening_time_str, categories_str, rating,
                         delivery_time, delivery_cost, minimum_order]

            if temp_data in store:
                logging.info("restaurant's data.bson already exists")

            else:
                store.append(temp_data)
                write_csv(f_name, temp_data)

            # back to main tab
            driver.switch_to.window(parent)
            time.sleep(1)

            if ind == 4:
                break

        except Exception as e:
            continue

    return store


def write_csv(name: str, row):
    with open(f'{name}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def create_csv(name: str):
    with open(f'{name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ['Postcode', 'Name', 'Address', 'Opening Times', 'Categories', 'Rating', 'Delivery Time',
                 'Delivery Cost', 'Minimum Order']
        writer.writerow(field)


if __name__ == '__main__':

    ch_driver = config_driver()
    post_codes = open('all_postcodes.txt', "r")
    logging.info('Script start running ...')
    file_name = f'data_{random.randint(1, 999999)}'
    create_csv(file_name)
    logging.info(f'<{file_name}> file is created to store data.bson actively')
    all_data = []

    for code in post_codes:
        code = code.strip()
        if code != "":
            data = scanner(ch_driver, code, all_data, file_name)
            all_data = data

    ch_driver.close()
    logging.info(f'Script executed successfully and data.bson is saved to <{file_name}.csv>')
