# import csv
# import logging
# import os
# import subprocess
# import time
# from datetime import date
#
# import pandas as pd
# import xlwings as xw
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
#
# import undetected_chromedriver as uc
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

#
LOGIN_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/login"
USERNMAE = "la-165095"
PASSWORD = "Snowing23#"
SEARCH_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/search"
#
#
#
# def config_driver():
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument("lang=en-GB")
#     chrome_options.add_argument('--ignore-certificate-errors')
#     chrome_options.add_argument('--allow-running-insecure-content')
#     chrome_options.add_argument("--disable-extensions")
#     chrome_options.add_argument("--proxy-server='direct://'")
#     chrome_options.add_argument("--proxy-bypass-list=*")
#     chrome_options.add_argument("--start-maximized")
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument("--log-level=3")
#     # driver = webdriver.Chrome(options=chrome_options)
#     driver = uc.Chrome(executable_path='chromedriver', options=chrome_options)
#     return driver
#
#
# def login(driver):
#     driver.get(INIT_URL)
#     time.sleep(10000)
#     # driver.find_element(By.ID, 'dateInput').clear()
#     # time.sleep(1)
#     # driver.find_element(By.ID, 'dateInput').send_keys('08/31/23')
#     # driver.find_element(By.XPATH, "//label[normalize-space()='Rancho Park']").click()
#     # time.sleep(10)
#     # driver.find_element(By.XPATH, "//button[normalize-space()='Search All']").click()
#     # time.sleep(10)
#
#     driver.find_element(By.XPATH, "//input[@title='Enter User Name']").send_keys(USERNMAE)
#     driver.find_element(By.XPATH, "//input[@title='Enter Password']").send_keys(PASSWORD)
#     time.sleep(5)
#     driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
#     time.sleep(10)
#
#
# def run():
#     driver = config_driver()
#     # login(driver)
#     driver.get('https://cityoflapcp.ezlinksgolf.com/index.html#/login')
#     time.sleep(100)
#
#
# if __name__ == '__main__':
#     run()

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


def config_uc_driver():
    return uc.Chrome(headless=False, use_subprocess=False, driver_executable_path='chromedriver.exe')


def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter User Name']").send_keys(USERNMAE)
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter Password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)


def search(driver):
    driver.get(SEARCH_URL)
    # driver.find_element(By.ID, 'dateInput').send_keys('08/31/23')
    time.sleep(5)
    element = driver.find_element(By.CSS_SELECTOR, '.search-clear-all')
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)
    element = driver.find_element(By.XPATH, "//label[@id='courseLabel_Rancho Park']")
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)

    v = "//div[@on-handle-up='ec.onTeeTimeFilterHandleUp()']//div[@class='ngrs-handle ngrs-handle-min']//i"
    r = driver.find_element(By.XPATH, v)
    print(r)

    while True:
        ActionChains(driver).drag_and_drop_by_offset(r, 100, 200).perform()
        time.sleep(5)






def run():
    driver = config_uc_driver()
    login(driver)
    search(driver)
    # login(driver)
    # driver.get('https://cityoflapcp.ezlinksgolf.com/index.html#/login')


if __name__ == '__main__':
    run()
