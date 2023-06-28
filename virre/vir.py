import csv
import datetime
import subprocess
import time

import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

# install dependencies
subprocess.check_call(['pip', 'install', 'fake_useragent'])
subprocess.check_call(['pip', 'install', 'selenium'])


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
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def csv_file_init(file_name: str):
    df = pd.DataFrame(columns=["Nimi", "Rekisteröintiajankohta", "Puhelin", "Sähköposti"])
    df.to_csv(file_name, index=False)
    print(f'{file_name} created successfully.')


def write_csv(file_name: str, new_data: dict):
    df = pd.DataFrame(new_data)
    df.to_csv(file_name, mode='a', header=False, index=False)


def validate_date(date_text: str):
    try:
        format = "%d.%m.%Y"
        datetime.datetime.strptime(date_text, format)
    except ValueError:
        print("Incorrect data format, should be dd.mm.YYYY")
        exit()


def take_input() -> (str, str):
    start_date = str(input('Enter start date (format: dd.mm.YYYY): ')).strip()
    validate_date(start_date)
    end_date = str(input('Enter end date (format: dd.mm.YYYY): ')).strip()
    validate_date(end_date)
    return start_date, end_date
    # return '01.06.2023', '02.06.2023'


def search(driver: webdriver.Chrome, start_date: str, end_date: str) -> webdriver.Chrome:
    while True:
        try:
            driver.get('https://virre.prh.fi/novus/registeredNotifications')
            driver.find_element(By.ID, 'startDate').clear()
            driver.find_element(By.ID, 'startDate').send_keys(start_date)
            driver.find_element(By.ID, 'endDate').clear()
            driver.find_element(By.ID, 'endDate').send_keys(end_date)
            select = Select(driver.find_element(By.ID, "registrationTypeCode"))
            select.select_by_value('kltu.U')
            driver.find_element(By.ID, '_eventId_search').click()
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'foundRegisteredNotifications')))
            return driver
        except:
            pass


def get_details_pages(driver: webdriver.Chrome) -> list:
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//a[@data-dt-idx="8"]')))
    last_page = driver.find_element(By.XPATH, '//a[@data-dt-idx="8"]').text
    hrefs = []
    for page_num in range(int(last_page)):
        try:
            a_tags = driver.find_elements(By.XPATH, '//td[@class="sorting_1"]//b//a')
            for ind, a_tag in enumerate(a_tags):
                hrefs.append(a_tag.get_attribute('href'))
            driver.find_element(By.XPATH, '//a[@data-dt-idx="9"]').click()
            time.sleep(1)
            print(f'Extracted details url from page {page_num + 1}')
        except:
            pass

    return hrefs


def scrapper():
    print('-----------------------------------------------------')
    print('Script starts running ...')
    start_date, end_date = take_input()
    file_name = f'data_{datetime.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.csv'
    csv_file_init(file_name)
    driver = config_driver()
    driver = search(driver, start_date, end_date)
    hrefs = get_details_pages(driver)
    page = 0
    while True:
        driver.get(hrefs[page])
        name, reg_number, phone, email = '', '', '', ''
        for i in range(20):
            try:
                header_xp = f'//tbody/tr[{i + 1}]/td[1]'
                value_xp = f'//tbody/tr[{i + 1}]/td[2]'
                header = driver.find_element(By.XPATH, header_xp).text
                if header == 'Nimi':
                    name = driver.find_element(By.XPATH, value_xp).text
                elif header == 'Rekisteröintiajankohta':
                    reg_number = driver.find_element(By.XPATH, value_xp).text
                elif header == 'Puhelin':
                    phone = driver.find_element(By.XPATH, value_xp).text
                elif header == 'Sähköposti':
                    email = driver.find_element(By.XPATH, value_xp).text
            except Exception as e:
                pass

        if name == '':
            driver = config_driver()
            search(driver, start_date, end_date)
            continue
        else:
            page += 1

        write_csv(file_name, {
            'Nimi': [name],
            'Rekisteröintiajankohta': [reg_number],
            'Puhelin': [phone],
            'Sähköposti': [email],
        })
        print(f'--> {page}. {name} inserted')

        if page + 1 >= len(hrefs):
            break

    print('Execution done!')


if __name__ == '__main__':
    scrapper()
