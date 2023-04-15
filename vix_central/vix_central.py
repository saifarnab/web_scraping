import time

import pandas as pd
import xlsxwriter as xlsxwriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    driver = webdriver.Chrome()
    if maximize_window is True:
        driver.maximize_window()
    return driver


def scanner():
    wb = xlsxwriter.Workbook("data.xlsx")
    sheet1 = wb.add_worksheet("results")

    website = 'http://vixcentral.com/historical?days=30'

    # define 'driver' variable
    driver = config_driver(False)
    driver.get(website)

    historical_prices = driver.find_element(By.XPATH, "//a[@id='ui-id-9']")
    historical_prices.click()
    time.sleep(1)
    date_input = driver.find_element(By.XPATH, '//input[@id="date1"]')
    date_input.clear()
    date_input.send_keys('January 6, 2014')
    time.sleep(1)
    get_price = driver.find_element(By.XPATH, '//button[@id="b4"]')
    get_price.click()
    time.sleep(2)

    data = []
    for i in range(10000):
        try:
            tspan = driver.find_elements(By.XPATH,
                                         "//*[local-name()='svg']//*[local-name()='tspan' and @class='highcharts-text-outline']")
            tspan.reverse()
            temp = []
            date_val = driver.find_element(By.XPATH, '//input[@id="date1"]').get_attribute('value')
            temp.append(date_val)
            temp2 = []
            for item in tspan:
                if item.text.strip() != "":
                    ActionChains(driver).move_to_element(item).perform()
                    temp2.append(item.text.strip())

            temp2.reverse()
            temp = temp + temp2[:7]

            expiration = driver.find_element(By.XPATH,
                                             "//*[local-name()='svg']//*[local-name()='g' and @class='highcharts-label highcharts-tooltip highcharts-color-0']//*[name()='text']//*[name()='tspan'][4]")

            temp.append(expiration.text.strip().split(' ')[-1])
            loop_breaker = date_val.strip()
            if loop_breaker == 'April 14, 2023':
                break
            next_date = driver.find_element(By.XPATH, "//button[@id='bnext']")
            next_date.click()
            time.sleep(1)
            print(f"Extracted date for the date of --> {date_val}  i value --> {i}--> length = {len(temp)}")
            if len(temp) <= 9:
                data.append(temp)
            else:
                print(f"ERROR --> {date_val} --> length = {len(temp)}")
        except Exception as e:
            print("Exception ", e)
    return data


if __name__ == '__main__':

    data = scanner()
    columns = ['Date', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'Days to expiration']
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(f"data.xlsx", index=False)
