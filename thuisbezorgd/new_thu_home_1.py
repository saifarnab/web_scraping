import csv
import logging
import math
import os
import subprocess
import time

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
    chrome_options.add_argument('--headless')
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


def scanner(driver, postcode, store, f_name):
    parent = driver.window_handles[0]
    logging.info(f'start loading url for <{postcode}> postcode')
    driver.get('https://www.thuisbezorgd.nl/' + postcode)
    time.sleep(3)
    if postcode_validation(driver, postcode) is False:
        return []
    driver.switch_to.default_content()
    try:
        driver.find_element(By.CSS_SELECTOR, '#cf-bubbles')
        print('cloud flare blocking')
    except Exception as e:
        pass
    wait_until_find_element(driver, By.XPATH, '//h1[@data-qa="restaurant-list-header"]')
    handle_cookies_popup(driver)

    # load the page completely by scrolling bottom
    start_time = time.time()
    logging.info('--> rendering places ...')
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(parent)
    scroll_down_page(driver)
    time.sleep(1)
    logging.info(f"{math.ceil(time.time() - start_time)}s to render all the places")

    # iterate each restaurant
    wait_until_find_element(driver, By.XPATH, '//a[@class="_9NUh1 qT7x_"]')
    restaurants = driver.find_elements(By.XPATH, '//a[@class="_9NUh1 qT7x_"]')
    logging.info(f"{len(restaurants)} places found for {postcode} location key")
    if len(restaurants) < 1:
        return []

    # get child tab
    child = driver.window_handles[1]
    for ind, item in enumerate(restaurants):

        try:
            start_time = time.time()
            # extract name, rating, reviews & details page link
            name = item.find_element(By.XPATH, './/h3[@data-qa="restaurant-info-name"]').text
            details_page_link = item.get_attribute('href')

            # check existence in csv
            csv_data = check_existence(f_name, 'Product Url', details_page_link)
            if csv_data is not None:
                temp_data = [postcode, name, csv_data['Address'], csv_data['Opening Times'], csv_data['Categories'],
                             csv_data['Rating'], csv_data['Delivery Time'], csv_data['Delivery Cost'],
                             csv_data['Minimum Order'], details_page_link]
                write_csv(f_name, temp_data)
                logging.info(
                    f"---> {ind + 1}. <{name}> restaurant's data is extracted!- required time <{math.ceil(time.time() - start_time)}s>")
                continue

            # Open a new window & Switch to the new window
            driver.switch_to.window(child)
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
                i_button = driver.find_element(By.XPATH, '//span[@data-qa="restaurant-header-action-info"]')
                i_button.click()
                time.sleep(4)
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
                    wait_until_find_element(driver, By.XPATH,
                                            '//div[@data-qa="restaurant-info-modal-info-address-element"]')
                    wait_until_find_element(driver, By.XPATH, '//b[@data-qa="text"]')
                    addresses = driver.find_elements(By.XPATH,
                                                     '//div[@data-qa="restaurant-info-modal-info-address-element"]//div['
                                                     '@data-qa="text"]')

                    for addr in addresses:
                        if addr.text != '':
                            address_str += f"{addr.text}, "
                except Exception as e:
                    pass

                # extract opening time
                opening_time_str = ''
                try:
                    wait_until_find_element(driver, By.XPATH,
                                            '//div[@data-qa="restaurant-info-modal-info-shipping-times-element-element'
                                            '"]//div[@class="_1sMed _1wlHd _2cDMI"]')
                    opening_times = driver.find_elements(By.XPATH,
                                                         '//div[@data-qa="restaurant-info-modal-info-shipping-times'
                                                         '-element-element"]//div[@class="_1sMed _1wlHd _2cDMI"]')

                    for opening_time_ind, opening_time_item in enumerate(opening_times):
                        elements = opening_time_item.find_elements(By.XPATH, './/div[@data-qa="text"]')
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
                                                 '//div[@data-qa="restaurant-info-modal-reviews-rating"]//div[@class="_50YZr _3-Fnx"]').text
                    review = driver.find_element(By.XPATH,
                                                 '//div[@class="_2oup6D"]//div[@class="Tcels"][1]').text.replace('\n',
                                                                                                                 '')
                    rating = f"{rating.strip()}{review.strip()}"
                    if rating[0:3] == rating[3:6]:
                        rating = rating[3:]
                    if rating[1] != ',':
                        rating = rating[0] + ',' + rating[1:]
                    rating = rating[0:3] + ", " + rating[3:]
                except Exception as ex:
                    rating = ''

            # extracting delivery time
            try:
                delivery_time = driver.find_element(By.XPATH, '//div[@data-qa="shipping-time-indicator-content"]').text
            except Exception as e:
                delivery_time = ''

            # extracting delivery cost
            try:
                delivery_cost = driver.find_element(
                    By.XPATH, '//div[@data-qa="delivery-costs-indicator"]//span[@class="_2PRj3E"]').text
            except Exception as e:
                delivery_cost = ''

            # extracting minimum order
            try:
                minimum_order = driver.find_element(
                    By.XPATH, '//div[@data-qa="mov-indicator-content"]//span[@class="_2PRj3E"]').text
            except Exception as e:
                minimum_order = ''

            temp_data = [postcode, name, address_str, opening_time_str, categories_str, rating,
                         delivery_time, delivery_cost, minimum_order, details_page_link]

            if temp_data in store:
                logging.info("restaurant's data already exists")

            else:
                # store.append(temp_data)
                write_csv(f_name, temp_data)
                logging.info(
                    f"---> {ind + 1}. <{name}> restaurant's data is extracted!- required time <{math.ceil(time.time() - start_time)}s>")

            # back to main tab
            driver.switch_to.window(parent)
            time.sleep(1)

        except Exception as e:
            print(e)
            continue

    return store


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


def check_existence(name, column_name, value):
    with open(f'{name}.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[column_name] == value:
                return row
    return None


def run():
    ch_driver = config_uc_driver()
    post_codes = open('ofc_postcodes.txt', "r")
    logging.info('Script start running ...')
    file_name = f'1000-1015'
    create_csv(file_name)
    logging.info(f'<{file_name}> file is created to store data actively')
    all_data = []

    for code in post_codes:
        code = code.strip()
        if code != "":
            data = scanner(ch_driver, code, all_data, file_name)
            all_data = data

    ch_driver.close()
    logging.info(f'Script executed successfully and data is saved to <{file_name}.csv>')


if __name__ == "__main__":
    run()