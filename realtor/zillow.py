import csv
import subprocess
import sys
import time
from os.path import exists

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from user_agent import generate_user_agent

# install dependencies
subprocess.check_call(['pip', 'install', 'user_agent'])
subprocess.check_call(['pip', 'install', 'selenium'])


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={generate_user_agent()}')
    return webdriver.Chrome(options=chrome_options)


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


def check_existence(file_name: str, new_row: list) -> bool:

    with open(file_name, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if line and new_row[3].strip() == line[3].strip():
                return True

    return False


def write_csv(file_name: str, new_row: list) -> bool:
    new_row[12] = new_row[12].replace('%20', '')
    add_hyperlink = f'=HYPERLINK("{new_row[12]}","{new_row[12]}")'
    new_row[12] = add_hyperlink

    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)
    print('--> New property added.')
    return True


def get_properties_data(filename: str) -> list:
    try:
        file_data = open(filename, "r")
        return list(csv.reader(file_data, delimiter=","))[1:]
    except Exception as e:
        print('Failed to read csv')
        exit()


def handle_captcha(driver):
    try:
        print('Handling captcha perimeter X')
        open_window_elem = "#px-captcha"
        x = int(driver.find_element(By.CSS_SELECTOR, open_window_elem).location['x'])
        y = int(driver.find_element(By.CSS_SELECTOR, open_window_elem).location['y'])
        width = int(driver.find_element(By.CSS_SELECTOR, open_window_elem).size['width'])
        height = int(driver.find_element(By.CSS_SELECTOR, open_window_elem).size['height'])

        action = ActionChains(driver)
        action.move_by_offset(x + width / 2, y + height / 2)
        action.click_and_hold()
        time.sleep(1)
        action.perform()
        time.sleep(11)
    except Exception as e:
        pass


def close_program(msg: str):
    print(msg)
    print('Script successfully executed!')
    exit()


def scrapper(filename: str):
    print('---------------------------******----------------------')
    print('Script starts ...')
    properties_data = get_properties_data(filename)
    zillow_filename = f'zillow_{filename}'
    csv_file_init(zillow_filename)
    pointer = 0
    while pointer < len(properties_data):
        if check_existence(zillow_filename, properties_data[pointer]) is True:
            print('Property already available, ignoring..')
            pointer += 1
            continue
        address = properties_data[pointer][3]  # take address from the properties list
        driver = config_driver()
        driver.get(f'https://www.zillow.com/homes/{address}')
        time.sleep(1)
        if 'captchaPerimeterX' in driver.current_url:
            handle_captcha(driver)
            continue

        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//button[@class="ds-close-lightbox-icon hc-back-to-list"]')))
        except Exception as e:
            print(driver.current_url)
            print('Zillow link not found')
            row = properties_data[pointer]
            row.append('')
            row.append('')
            write_csv(zillow_filename, row)
            pointer += 1
            driver.close()
            time.sleep(1)

        try:
            zillow_url = driver.current_url
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//span[@class="RCFAgentPhoneDesktopText__phoneNumber"]')))
            telephone = driver.find_element(By.XPATH, '//span[@class="RCFAgentPhoneDesktopText__phoneNumber"]').text
            if telephone in [None, '', ' ']:
                raise Exception('telephone number not found')
        except Exception as e:
            try:
                zillow_url = driver.current_url
                telephone = driver.find_element(By.XPATH, '//li[@class="ds-listing-agent-info-text"]').text
            except Exception as e:
                zillow_url = driver.current_url
                telephone = ''

        row = properties_data[pointer]
        row.append(zillow_url)
        row.append(telephone)
        write_csv(zillow_filename, row)
        pointer += 1
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
        print('Something went wrong, please run the script again')
