import logging
import subprocess
import pathlib
import time
from datetime import date

import pyodbc
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


def config_driver(maximize_window: bool) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    if maximize_window is True:
        driver.maximize_window()
    return driver


def ms_access_exist(game_date, game) -> bool:
    conn = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + f'{pathlib.Path(__file__).parent.resolve()}\gamedb.accdb;')
    cursor = conn.cursor()
    cursor.execute('select * from data')
    for row in cursor.fetchall():
        if row[1] == game_date and row[2] == game:
            conn.close()
            return True

    conn.close()
    return False


def ms_access_insert(game_date, game, home, ht_home, ht_away, ht_draw, home_on, home_off, home_da, away_on, away_off,
                     away_da, ht_score):
    conn = pyodbc.connect(
        r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\User\Documents\goal\gamedb.accdb;')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO data (GameDate, Game, Home, HTHome, HTAway, HTDraw, HomeOn, HomeOff, HomeDA, AwayOn, AwayOff, AwayDA, HTScore) \
                    VALUES ('{game_date}', '{game}', '{home}', '{ht_home}', '{ht_away}', '{ht_draw}', '{home_on}', '{home_off}', '{home_da}', '{away_on}', '{away_off}', '{away_da}', '{ht_score}')")
    conn.commit()
    conn.close()


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

            # get to the live game section
            driver.get('https://live.goalprofits.com/')
            live_games_button = driver.find_element(By.XPATH, '//a[@href="#live"]')
            live_games_button.click()
            time.sleep(1)
            live_games_button.click()
            time.sleep(1)

            # find available live games
            table_elements = driver.find_elements(By.XPATH, '//div[@id="html2"]//table')
            # wait till 60s if no live games are available
            if len(table_elements) == 0:
                time.sleep(60)
                logging.info('--> no live games are playing, waiting 60s for next try.')
                continue

            # iterate each tr
            for table_ind in range(len(table_elements)):
                tr_elements = table_elements[table_ind].find_elements(By.XPATH, './/tbody//tr')
                tr_ind = 0

                # iterate each td
                for ind in range(int(len(tr_elements) / 2)):
                    td_elements = tr_elements[tr_ind].find_elements(By.XPATH, ".//td")
                    current_date = date.today().strftime('%d/%m/%y')
                    try:
                        game_time = td_elements[0].text.strip()
                        logging.info(f'game_time --> {game_time}')
                    except Exception as exx:
                        game_time = 'N/A'

                    # if game time is not HT then return
                    if game_time != 'HT':
                        tr_ind += 2
                        continue

                    # extract required data from 1st tr

                    team1 = td_elements[1].text.index('(')
                    team1 = td_elements[1].text[:team1].strip()
                    logging.info(f'team1 --> {team1}')

                    try:
                        ht_score = td_elements[3].text.split('\n')[0]
                        logging.info(f'ht_score --> {ht_score}')
                    except Exception as exx:
                        ht_score = 'N/A'

                    try:
                        ht_home = td_elements[21].text.replace('\n', '').split('%')[0].split(' ')[1].strip()
                        logging.info(f'ht_home --> {ht_home}')
                    except Exception as exx:
                        ht_home = 'N/A'

                    try:
                        ht_away = td_elements[21].text.replace('\n', '').split('%')[2].split(' ')[1].strip()
                        logging.info(f'ht_away --> {ht_away}')
                    except Exception as exx:
                        ht_away = 'N/A'

                    try:
                        ht_draw = td_elements[21].text.replace('\n', '').split('%')[1].split(' ')[1].strip()
                        logging.info(f'ht_draw --> {ht_draw}')
                    except Exception as exx:
                        ht_draw = 'N/A'

                    try:
                        home_on = td_elements[4].text
                        logging.info(f'home_on --> {home_on}')
                    except Exception as exx:
                        home_on = 'N/A'

                    try:
                        home_off = td_elements[5].text
                        logging.info(f'home_off --> {home_off}')
                    except Exception as exx:
                        home_off = 'N/A'

                    try:
                        home_da = td_elements[10].text
                        logging.info(f'home_da --> {home_da}')
                    except Exception as exx:
                        home_da = 'N/A'

                    logging.info('extracted required data from 1st tr')

                    # extract required data from 2nd tr
                    td_elements2 = tr_elements[tr_ind + 1].find_elements(By.XPATH, ".//td")

                    team2 = td_elements2[0].text.index('(')
                    team2 = td_elements2[0].text[:team2].strip()
                    logging.info(f'team2 --> {team2}')

                    try:
                        away_on = td_elements2[1].text
                        logging.info(f'away_on --> {away_on}')
                    except Exception as exx:
                        away_on = 'N/A'

                    try:
                        away_off = td_elements2[2].text
                        logging.info(f'away_off --> {away_off}')
                    except Exception as exx:
                        away_off = 'N/A'

                    try:
                        away_da = td_elements2[7].text
                        logging.info(f'away_da --> {away_da}')
                    except Exception as exx:
                        away_da = 'N/A'

                    logging.info('extracted required data from 2nd tr')

                    game = team1 + ' v ' + team2
                    logging.info(f'game --> {game}')

                    # return if data already avalaible in accdb
                    if ms_access_exist(current_date, game) is True:
                        logging.info('data already avalaible in accdb')
                        continue

                    # extract data from i button which will open a modal
                    td_elements[2].find_element(By.XPATH, './/a[2]').click()
                    logging.info(f'i button 1st click done')
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//a[@id="pregame-tab"]').click()
                    logging.info(f'i button 2nd click done')
                    time.sleep(1)
                    try:
                        home = driver.find_elements(By.XPATH,
                                                    '//table[@class="table borderless table-striped score-table"]//span[@class="d-block font13 text-nowrap"]')[
                            0].text.split(':')[1].strip()
                        logging.info(f'home --> {home}')
                    except Exception as exx:
                        home = 'N/A'

                        # close the modal opened by i button
                    close_buttons = driver.find_elements(By.XPATH, '//button[@class="close"]')
                    for close_button in close_buttons:
                        try:
                            close_button.click()
                            logging.info('clieck close button to close the modal')
                        except Exception as e:
                            continue

                    time.sleep(1)

                    # insert data to accdb
                    ms_access_insert(current_date, game, home, ht_home, ht_away, ht_draw, home_on,
                                     home_off, home_da, away_on, away_off, away_da, ht_score)
                    logging.info('stored in access db')

                    tr_ind += 2
                    logging.info(f'--> <{game}> data is fetched and stored to accdb!')

        except Exception as ex:
            continue


if __name__ == '__main__':
    logging.info('Script start running ...')
    data = scanner()

