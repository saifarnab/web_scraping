import csv
import datetime
import subprocess
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# install dependencies
# subprocess.check_call(['pip', 'install', 'selenium'])
# subprocess.check_call(['pip', 'install', 'pandas'])


def config_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("lang=en-GB")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--log-level=3")
    # chrome_options.add_argument(f'user-agent={UserAgent().random}')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def read_emails(file_name: str):
    try:
        df = pd.read_csv(file_name)
        return df['Emails']
    except Exception as e:
        print(e)
        print('emails.csv missing, note: csv only contains email without header')
        exit()


def add_to_csv_cell(filename, row_index, column_index, value, delimiter=','):
    # Read the entire CSV file
    with open(filename, 'r', newline='') as csvfile:
        rows = list(csv.reader(csvfile, delimiter=delimiter))

    # Check if the row index is valid
    if 0 <= row_index < len(rows):
        row = rows[row_index]

        # Check if the column index is valid
        if 0 <= column_index < len(row):
            row[column_index] = value
        else:
            print(f"Column index {column_index} is out of range.")
            return
    else:
        print(f"Row index {row_index} is out of range.")
        return

    # Write the updated rows back to the CSV file
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=delimiter)
        csvwriter.writerows(rows)


def scrapper():
    print('-----------------------------------------------------')
    print('Script starts running ...')
    file_name = f'emails.csv'
    emails = read_emails(file_name)
    driver = config_driver()
    driver.get('https://accounts.jacksonhewitt.com/Account/SignUp')
    counter = 1
    for ind, email in enumerate(emails):
        driver.find_element(By.ID, 'Email').clear()
        driver.find_element(By.ID, 'Email').send_keys(str(email).strip())
        time.sleep(3)
        style = driver.find_element(By.XPATH, '//li[@id="EmailCriteriaNotAvailable"]').get_attribute('style')
        if 'block' in style:
            add_to_csv_cell(file_name, counter, 1, email)
            counter += 1
            print(f'--> {email} inserted as valid email')
        else:
            print(f'--> {email} is an invalid email')

    print('Execution done!')


if __name__ == '__main__':
    scrapper()