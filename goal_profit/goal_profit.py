import csv
import logging
import random
import time

import pandas as pd
import xlsxwriter as xlsxwriter
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.action_chains import ActionChains

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    chrome_options = Options()
    # chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})
    # chrome_options.page_load_strategy = 'eager'
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    if maximize_window is True:
        driver.maximize_window()
    return driver


def create_csv():
    with open(f'{file_name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ['ID', 'Date', 'Game', 'Home', 'HT Home', 'HT Away', 'HT Draw', 'Home On', 'Home Off', 'Home DA',
                 'Away On', 'Away Off', 'Away DA', 'HT Score']
        writer.writerow(field)


def write_csv(row):
    with open(f'{file_name}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def check_back(c_date, game: str) -> bool:
    with open(f'{file_name}.csv', 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[1] == c_date and row[2] == game:
                return True

    return False


def scanner():
    # define 'driver' variable
    driver = config_driver(True)
    driver.get('https://live.goalprofits.com/')
    username_input_button = driver.find_element(By.XPATH, '//input[@id="wlm_form_field_log"]')
    username_input_button.clear()
    username_input_button.send_keys("dennis.peibst@googlemail.com")
    pass_input_button = driver.find_element(By.XPATH, '//input[@id="wlm_form_field_pwd"]')
    pass_input_button.clear()
    pass_input_button.send_keys("Freelancer1")
    driver.find_element(By.XPATH, '//input[@id="wlm_form_field_wp-submit"]').click()
    time.sleep(2)

    sl = 1
    while True:

        try:
            driver.get('https://live.goalprofits.com/')
            live_games_button = driver.find_element(By.XPATH, '//a[@href="#live"]')
            live_games_button.click()
            time.sleep(1)
            live_games_button.click()
            time.sleep(1)

            table_elements = driver.find_elements(By.XPATH, '//div[@id="html2"]//table')
            for table_ind in range(len(table_elements)):
                tr_elements = table_elements[table_ind].find_elements(By.XPATH, './/tbody//tr')
                tr_ind = 0
                for ind in range(int(len(tr_elements) / 2)):
                    # home row
                    td_elements = tr_elements[tr_ind].find_elements(By.XPATH, ".//td")
                    current_date = date.today().strftime('%d/%m/%y')
                    game_time = td_elements[0].text.strip()
                    # if game_time != 'HT':
                    #     tr_ind += 2
                    #     continue

                    team1 = td_elements[1].text.index('(')
                    team1 = td_elements[1].text[:team1].strip()

                    ht_score = td_elements[3].text.split('\n')[0]
                    ht_home = td_elements[21].text.replace('\n', '').split('%')[0].split(' ')[1].strip()
                    ht_away = td_elements[21].text.replace('\n', '').split('%')[2].split(' ')[1].strip()
                    ht_draw = td_elements[21].text.replace('\n', '').split('%')[1].split(' ')[1].strip()
                    home_on = td_elements[4].text
                    home_off = td_elements[5].text
                    home_da = td_elements[10].text

                    # away row

                    td_elements2 = tr_elements[tr_ind + 1].find_elements(By.XPATH, ".//td")
                    team2 = td_elements2[0].text.index('(')
                    team2 = td_elements2[0].text[:team2].strip()

                    away_on = td_elements2[1].text
                    away_off = td_elements2[2].text
                    away_da = td_elements2[7].text

                    game = team1 + ' v ' + team2

                    print(f'-----------------{ind}----------------------')
                    td_elements[2].find_element(By.XPATH, './/a[2]').click()
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//a[@id="pregame-tab"]').click()
                    time.sleep(1)
                    home = driver.find_elements(By.XPATH, '//table[@class="table borderless table-striped score-table"]//span[@class="d-block font13 text-nowrap"]')[0].text.split(':')[1].strip()

                    temp = [sl, current_date, game, home, ht_home, ht_away, ht_draw, home_on, home_off,
                            home_da, away_on, away_off, away_da, ht_score]

                    if check_back(current_date, game) is False:
                        write_csv(temp)
                    sl += 1
                    logging.info(f'--> <{game}> data is fetched!')

        except Exception as ex:
            print(ex)
            exit()

    return []


# //table[@class="table borderless table-striped score-table"]//span[@class="d-block font13 text-nowrap"]

if __name__ == '__main__':
    logging.info('Script start running ...')
    file_name = f'data'
    create_csv()
    data = scanner()
