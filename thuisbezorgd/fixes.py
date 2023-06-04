import csv
import logging
import math
import os
import subprocess
import time

import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

# install dependencies
# subprocess.check_call(['pip', 'install', 'undetected-chromedriver'])
# subprocess.check_call(['pip', 'install', 'selenium'])

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


# chrome driver configuration
def config_uc_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument('--headless')
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
def scroll_down_page(driver):
    pre_len = len(driver.find_elements(By.XPATH, '//a[@class="_9NUh1 qT7x_"]'))
    html = driver.find_element(By.TAG_NAME, 'html')
    counter = 0
    while len(driver.find_elements(By.XPATH, "//footer")) < 1:
        html.send_keys(Keys.ARROW_DOWN)
        post_len = len(driver.find_elements(By.XPATH, '//a[@class="_9NUh1 qT7x_"]'))
        counter += 1
        if counter % 50 == 0:
            if pre_len == post_len:
                break


# check valid postcode
def postcode_validation(driver, postcode) -> bool:
    while True:
        try:
            if f'/{postcode}' in driver.current_url:
                try:
                    wait_until_find_element(driver, By.XPATH, '//iframe')
                    iframe = driver.find_element(By.XPATH, '//iframe')
                    driver.switch_to.frame(iframe)
                    wait_until_find_element(driver, By.XPATH, '//input[@type="checkbox"]')
                    driver.find_element(By.XPATH, '//input[@type="checkbox"]').click()
                    driver.switch_to.default_content()
                    time.sleep(10)
                    if driver.current_url == 'https://www.thuisbezorgd.nl/' + postcode:
                        continue
                    logging.info('bypass cloud-flare success')
                except Exception as e:
                    driver.save_screenshot('demo.png')
                    time.sleep(10)
            elif "redirected" in driver.current_url:
                logging.info(f'no data available for `{postcode}` postcode')
                return False
            elif "menu" in driver.current_url:
                print('retrying...')
                time.sleep(10)

            else:
                time.sleep(10)

            break
        except Exception as e:
            print(e)
            logging.error('Exception occurs, retrying.. ')
            continue

    return True


def scanner():
    data_frame = pd.read_csv('fix.csv')
    for index, row in data_frame.iterrows():
        if str(row['Opening Times']) == 'nan':
            print(index, row['Product Url'])


        # write_csv('fix', [row['Postcode'], row['Name'], address_str, row['Opening Times'], row['Categories'],
        #                   row['Rating'], row['Delivery Time'], row['Delivery Cost'],
        #                   row['Minimum Order'], row['Product Url']])


def write_csv(name: str, row):
    with open(f'{name}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def create_csv(name: str):
    if os.path.exists(f'{name}.csv'):
        return
    with open(f'{name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ['Postcode', 'Name', 'Address', 'Opening Times', 'Categories', 'Rating', 'Delivery Time',
                 'Delivery Cost', 'Minimum Order', 'Product Url']
        writer.writerow(field)


def run():
    create_csv('fix')
    # ch_driver = config_uc_driver()
    scanner()
    logging.info(f'Script executed successfully')


if __name__ == "__main__":
    run()
