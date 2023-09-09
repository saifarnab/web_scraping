import csv
import logging
import os
import random
import time
from datetime import date

import pandas as pd
import xlwings as xw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# excel db path
GAMEDB = 'scrap2.xlsx'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def config_driver(maximize_window: bool) -> webdriver.Chrome:
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
    # driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)
    if maximize_window is True:
        driver.maximize_window()
    return driver


def check_excel_file() -> bool:
    if os.path.exists(GAMEDB):
        return True
    return False


def create_csv(filename: str):
    file_exists = os.path.isfile(filename)
    headers = ['Provider', 'SelectionName', 'MarketName', 'EventName', 'MarketType', 'BetType']
    if not file_exists:
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)


def get_last_data_from_csv(filename: str) -> list:
    try:
        df = pd.read_csv(filename)
        return df.iloc[-1].tolist()
    except:
        return []


def save_csv_data(filename: str, row: list):
    df = pd.read_csv(filename)
    new_row_df = pd.DataFrame([row], columns=df.columns)
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_csv(filename, index=False)


def get_first_blank_row():
    df = pd.read_excel(GAMEDB, sheet_name='Scrape', engine="openpyxl")
    return df.shape[0] + 1


def check_for_duplicate(data_row) -> bool:
    df = pd.read_excel(GAMEDB, sheet_name='Scrape', engine="openpyxl", skiprows=1)
    match = df.loc[(df['GameDate'] == data_row[0]) & (df['Game'] == data_row[1])]
    if not match.empty:
        return True
    else:
        return False


def insert_or_update_row(first_blank_row: int, new_data: list) -> bool:
    app = xw.App(visible=False)

    try:
        wb = xw.Book(GAMEDB)
        sheet = wb.sheets["Scrape"]
        new_data_strings = [str(value) for value in new_data]
        row_range = sheet.range(f"A{first_blank_row}:O{first_blank_row}")
        for cell, value in zip(row_range, new_data):
            cell.value = value
        wb.save()
        return True
    finally:
        app.quit()  # Close the hidden Excel application


def save_to_csv():
    # for HT 0-0
    try:
        df = pd.read_excel(GAMEDB, sheet_name='HT 0-0', skiprows=1)
        df = df[['Provider', 'SelectionName', 'MarketName', 'EventName', 'MarketType', 'BetType']]
        last_non_blank_row_index = df.last_valid_index()
        last_non_blank_row_data = df.iloc[last_non_blank_row_index]
        last_excel_row = last_non_blank_row_data.tolist()
        create_csv('HT 0-0.csv')
        last_csv_row = get_last_data_from_csv('HT 0-0.csv')
        if last_excel_row != last_csv_row:
            save_csv_data('HT 0-0.csv', last_excel_row)
    except:
        pass

    # for HT 0-1
    try:
        df = pd.read_excel(GAMEDB, sheet_name='HT 0-1', skiprows=1)
        df = df[['Provider', 'SelectionName', 'MarketName', 'EventName', 'MarketType', 'BetType']]
        last_non_blank_row_index = df.last_valid_index()
        last_non_blank_row_data = df.iloc[last_non_blank_row_index]
        last_excel_row = last_non_blank_row_data.tolist()
        create_csv('HT 0-1.csv')
        last_csv_row = get_last_data_from_csv('HT 0-1.csv')
        if last_excel_row != last_csv_row:
            save_csv_data('HT 0-1.csv', last_excel_row)
    except:
        pass

    # for HT 1-0
    try:
        df = pd.read_excel(GAMEDB, sheet_name='HT 1-0', skiprows=1)
        df = df[['Provider', 'SelectionName', 'MarketName', 'EventName', 'MarketType', 'BetType']]
        last_non_blank_row_index = df.last_valid_index()
        last_non_blank_row_data = df.iloc[last_non_blank_row_index]
        last_excel_row = last_non_blank_row_data.tolist()
        create_csv('HT 1-0.csv')
        last_csv_row = get_last_data_from_csv('HT 1-0.csv')
        if last_excel_row != last_csv_row:
            save_csv_data('HT 1-0.csv', last_excel_row)
    except:
        pass

    # for HT 1-1
    try:
        df = pd.read_excel(GAMEDB, sheet_name='HT 1-1', skiprows=1)
        df = df[['Provider', 'SelectionName', 'MarketName', 'EventName', 'MarketType', 'BetType']]
        last_non_blank_row_index = df.last_valid_index()
        last_non_blank_row_data = df.iloc[last_non_blank_row_index]
        last_excel_row = last_non_blank_row_data.tolist()
        create_csv('HT 1-1.csv')
        last_csv_row = get_last_data_from_csv('HT 1-1.csv')
        if last_excel_row != last_csv_row:
            save_csv_data('HT 1-1.csv', last_excel_row)
    except:
        pass


def scanner():
    # define 'driver' variable
    if check_excel_file() is False:
        return

    first_blank_row = get_first_blank_row()
    driver = config_driver(True)

    # iterate to extract game data
    while True:

        str_list = ["Time heals vs 1", "Dream big vs 2", "Stay strong vs 3", "Love wins vs 31", "Learn, grow vs 32", "Ok vs 4"]
        float_list = ["1.5", "3.14", "2.718", "0.99", '4.75', '9.0']

        current_date = date.today().strftime('%d/%m/%y')
        game = str_list[random.randint(0, 5)]
        home = float_list[random.randint(0, 5)]
        away = float_list[random.randint(0, 5)]
        draw = float_list[random.randint(0, 5)]
        ht_home = float_list[random.randint(0, 5)]
        ht_away = float_list[random.randint(0, 5)]
        ht_draw = float_list[random.randint(0, 5)]
        home_on = float_list[random.randint(0, 5)]
        home_off = float_list[random.randint(0, 5)]
        home_da = float_list[random.randint(0, 5)]
        away_on = float_list[random.randint(0, 5)]
        away_off = float_list[random.randint(0, 5)]
        away_da = float_list[random.randint(0, 5)]
        ht_score = float_list[random.randint(0, 5)]
        try:
            # insert data to gamedb

            data_row = [current_date.replace(':', ''), game.replace(':', ''), home.replace(':', ''),
                        away.replace(':', ''), draw.replace(':', ''), ht_home.replace(':', ''),
                        ht_away.replace(':', ''), ht_draw.replace(':', ''),
                        home_on.replace(':', ''), home_off.replace(':', ''), home_da.replace(':', ''),
                        away_on.replace(':', ''), away_off.replace(':', ''), away_da.replace(':', ''),
                        ht_score.replace(':', '')]
            print(data_row)
            if check_for_duplicate(data_row) is False:
                insert = insert_or_update_row(first_blank_row, data_row)
                first_blank_row += 1
                if insert is True:
                    logging.info(f'--> <{game}> data is fetched and stored to gamedb!')
                    time.sleep(5)
                    save_to_csv()
                else:
                    logging.info(f'--> <{game}> data is already exist in gamedb!')
                    save_to_csv()

        except Exception as ex:
            print(ex)
            break


if __name__ == '__main__':
    logging.info('----------------- Script start running ... -----------------')
    scanner()
