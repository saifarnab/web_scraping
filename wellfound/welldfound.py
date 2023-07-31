import os
import subprocess
import time
from io import BytesIO

import openpyxl
import pandas as pd
import requests
from PIL import Image
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import undetected_chromedriver as uc



def config_uc_driver() -> webdriver.Chrome:
    driver = uc.Chrome()
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f'user-agent={UserAgent().chrome}')
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument('--headless')
    return driver



def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument(f'user-agent={UserAgent().random}')
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver) -> bool:
    try:
        driver.get('https://wellfound.com/login')
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'user_email')))
        driver.find_element(By.ID, 'user_email').clear()
        driver.find_element(By.ID, 'user_email').send_keys('chad@nextlevelrecruiter.com')
        driver.find_element(By.ID, 'user_password').clear()
        driver.find_element(By.ID, 'user_password').send_keys('Automated123!')
        driver.find_element(By.XPATH, '//input[@name="commit"]').click()
        WebDriverWait(driver, 7).until(EC.visibility_of_element_located((By.XPATH, "//h1[normalize-space()='Search for jobs']")))
        driver.get('https://wellfound.com/jobs')
        time.sleep(3333)
        return True
    except Exception as e:
        time.sleep(3333)
        return False
    
    


def scrapper():
    driver = None
    while True:
        driver = config_uc_driver()
        login(driver)

    
    
    time.sleep(1000)

if __name__ == '__main__':
    scrapper()
