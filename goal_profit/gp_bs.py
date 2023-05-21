import csv
import logging
import subprocess
import time
from lxml import etree
from bs4 import BeautifulSoup
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# install dependencies
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'pyodbc'])

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def csv_file_init():
    try:
        with open('game.csv', 'x', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                ['GameDate', 'Game', 'Home', 'HTHome', 'HTAway', 'HTDraw', 'HomeOn', 'HomeOff', 'HomeDA', 'AwayOn',
                 'AwayOff', 'AwayDA', 'HTScore'])
            print('File created successfully.')
    except FileExistsError:
        pass


def check_existence(current_date, game: str) -> bool:
    with open('game.csv', "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if line and current_date == line[0] and game == line[1]:
                return True
    return False


def write_csv(game_date, game, home, ht_home, ht_away, ht_draw, home_on, home_off, home_da, away_on,
              away_off, away_da, ht_score) -> bool:
    new_row = [game_date, game, home, ht_home, ht_away, ht_draw, home_on, home_off, home_da, away_on, away_off, away_da,
               ht_score]

    with open('game.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)
    print('--> New game added.')
    return True


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    # driver.execute_cdp_cmd('Emulation.setScriptExecutionDisabled', {'value': True})
    if maximize_window is True:
        driver.maximize_window()
    return driver


def scanner():
    # define 'driver' variable
    driver = config_driver(True)
    driver.get('https://live.goalprofits.com/')

    # login to the site
    username_input_button = driver.find_element(By.XPATH, '//input[@id="wlm_form_field_log"]')
    username_input_button.clear()
    username_input_button.send_keys("dennis.peibst@googlemail.com")
    pass_input_button = driver.find_element(By.XPATH, '//input[@id="wlm_form_field_pwd"]')
    pass_input_button.clear()
    pass_input_button.send_keys("Freelancer1")
    driver.find_element(By.XPATH, '//input[@id="wlm_form_field_wp-submit"]').click()
    time.sleep(2)

    # iterate to extract game data
    while True:

        try:
            driver.get('https://live.goalprofits.com/')
            time.sleep(1)
            driver.find_element(By.XPATH, '//a[@href="#live"]').click()

            # find available live games
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            dom = etree.HTML(str(soup))
            table_elements = dom.xpath('//div[@id="html2"]//table')
            print(f'table elements ', len(table_elements))

            if len(table_elements) > 0:
                tr_elements = dom.xpath('//div[@id="html2"]//table//tbody//tr')
                print(f'tr elements ', len(tr_elements))
                tr_ind = 0

                for ind in range(int(len(tr_elements) / 2)):
                    td_elements = tr_elements[tr_ind].xpath(".//td")
                    print(td_elements)
                    current_date = date.today().strftime('%d/%m/%y')
                    try:
                        game_time = td_elements[0].text.strip()
                        print(game_time)
                    except Exception as exx:
                        print(exx)
                        game_time = 'N/A'



        except Exception as ex:
            continue


if __name__ == '__main__':
    logging.info('Script start running ...')
    csv_file_init()
    data = scanner()
