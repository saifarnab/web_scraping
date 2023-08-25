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

#
# INIT_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/login"
# USERNMAE = "la-165095"
# PASSWORD = "Snowing23#"
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
from selenium.webdriver.chrome.service import Service


def config_uc_driver():
    import undetected_chromedriver as uc
    driver = uc.Chrome(headless=False, use_subprocess=False, driver_executable_path='chrome')
    driver.get('https://golf.lacity.org/request_tt/')
    time.sleep(1000)
    return driver


def run():
    driver = uc.Chrome()
    # login(driver)
    # driver.get('https://cityoflapcp.ezlinksgolf.com/index.html#/login')


if __name__ == '__main__':
    run()
