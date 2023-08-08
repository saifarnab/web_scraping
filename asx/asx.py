import time

import openpyxl
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-miniimized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def append_to_excel(data):
    filename = 'asx_v2.xlsx'
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in data:
        sheet.append(row)
    workbook.save(filename)


def scrapper():
    df = pd.read_csv('asx.csv')
    driver = config_driver()
    counter = 1
    for index, row in df.iterrows():
        code = row['ASX code']
        company_name = row['Company name']
        driver.get(f'https://www.asx.com.au/markets/company/{code}')
        # driver.get(f'https://www.asx.com.au/markets/company/5EA')
        time.sleep(5)
        try:
            lis = driver.find_elements(By.XPATH, '//div[@class="m-b-3"]//ul//li')
            for li in lis:
                divs = li.find_elements(By.XPATH, './/div')
                name = divs[0].text.strip().split(' ')
                position = divs[1].text
                try:
                    address = driver.find_element(By.XPATH, '//tr[@class="m-b-2"][1]//td[1]').text
                except:
                    address = ''
                if len(name) == 3:
                    title = name[0]
                    firstname = name[1]
                    middle_name = ''
                    lastname = name[2]
                    append_to_excel([[company_name, code, address, title, firstname, middle_name, lastname, position]])
                elif len(name) == 4:
                    title = name[0]
                    firstname = name[1]
                    middle_name = name[2]
                    lastname = name[3]
                    append_to_excel([[company_name, code, address, title, firstname, middle_name, lastname, position]])
                elif len(name) > 4:
                    title = name[0]
                    firstname = name[1]
                    middle_name = name[2]
                    lastname = name[3:]
                    lastname = " ".join(str(item) for item in lastname)
                    append_to_excel([[company_name, code,address, title, firstname, middle_name, lastname, position]])
        except Exception as e:
            print(e)
            append_to_excel([[company_name, code, address, '', '', '', '', '']])

        print(f'{counter}. {company_name} inserted. ')
        counter += 1


if __name__ == '__main__':
    scrapper()
