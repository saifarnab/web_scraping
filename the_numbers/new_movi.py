import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


def config_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/96.0.4664.45 Safari/537.36')
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
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()
    return driver


def extract_franchises(driver):
    print('*********************** Script Starts **************************')
    print('Movie franchise extraction start ...')
    driver.get("https://www.the-numbers.com/movies/franchises")
    time.sleep(1)
    select = Select(driver.find_element(By.TAG_NAME, 'select'))
    select.select_by_visible_text('100')
    dataframe_1 = pd.DataFrame()
    last_page = int(
        driver.find_elements(By.CSS_SELECTOR, "#franchise_overview_paginate > span > a:nth-child(n)")[-1].text)
    for b in range(last_page):
        td = driver.find_elements(By.CSS_SELECTOR,
                                  "#franchise_overview > tbody > tr:nth-child(n) > td:nth-child(1) > b > a")
        for a in range(len(td)):
            fra_name = td[a].text
            fra_u = td[a].get_attribute("href")
            dic = {'Franchise': fra_name, 'fra_link': fra_u}
            dataframe_1 = pd.concat([dataframe_1, pd.DataFrame([dic])], ignore_index=True)
            print(f"Extracted franchise -> {fra_name}")

        driver.find_element(By.CSS_SELECTOR, "#franchise_overview_next").click()

    print(f"Franchises extraction completed!")
    print('----------------------------------------')
    return dataframe_1


def extract_movies(driver, franchises):
    print('Movie title & release date extraction start ...')

    dataframe_2 = pd.DataFrame()
    for d in range(len(franchises)):
        driver.get(franchises.fra_link[d])
        time.sleep(2)
        td = driver.find_elements(By.CSS_SELECTOR,
                                  "#franchise_movies_overview > tbody > tr:nth-child(n) > td:nth-child(2) > b > a")
        td1 = driver.find_elements(By.CSS_SELECTOR,
                                   "#franchise_movies_overview > tbody > tr:nth-child(n) > td.sorting_1")

        if len(td) < 2:
            continue
        for c in range(len(td)):
            try:
                if td[c].text.split(" ")[0] != "Untitled":
                    try:
                        date = td1[c].text.split(",")[-1]
                    except:
                        date = td1[c].text
                    dic = {'Franchise': franchises.Franchise[d], 'Movie_title': td[c].text, 'Release_date': date}
                    dataframe_2 = pd.concat([dataframe_2, pd.DataFrame([dic])], ignore_index=True)
                    print(f'{franchises.Franchise[d]} --> {td[c].text} {date}')

            except Exception:
                continue

    return dataframe_2


def extract_imdb(driver, movies):
    dataframe_3 = pd.DataFrame()
    print('-----------------------------------------')
    print('Extracting IMDB Data ...')

    for e in range(0, len(movies)):
        try:
            driver.get("https://www.imdb.com/?ref_=nv_home")
            time.sleep(2)
            inp = driver.find_element(By.CSS_SELECTOR, "#suggestion-search")
            movie_txt = movies.Movie_title[e]
            txt = movies.Movie_title[e] + " " + movies.Release_date[e]
            inp.send_keys(txt)
            inp.send_keys(Keys.ENTER)
            time.sleep(3)

            try:
                first_choice = driver.find_elements(By.XPATH, '//a[@class="ipc-metadata-list-summary-item__t"]')[0]
                first_choice.click()
                mo_title = driver.find_element(By.XPATH, '//h1[@data.bson-testid="hero__pageTitle"]//span').text
                imdb = driver.current_url.split('title')[1].split('?')[0][1:-1]
                dic = {'Franchise': movies.Franchise[e], 'Movie_title': mo_title,
                       'Release_Year': movies.Release_date[e],
                       'IMDB_id': imdb}

            except Exception as e:
                dic = {'Franchise': movies.Franchise[e], 'Movie_title': movie_txt,
                       'Release_Year': movies.Release_date[e],
                       'IMDB_id': 'NA'}

            print(f'{dic["Franchise"]} --> {dic["Movie_title"]} --> {dic["Release_Year"]} --> {dic["IMDB_id"]}')

            dataframe_3 = pd.concat([dataframe_3, pd.DataFrame([dic])], ignore_index=True)

        except Exception as e:
            continue
    return dataframe_3


if __name__ == '__main__':
    ch_driver = config_driver()
    franchises_df = extract_franchises(ch_driver)
    movies_df = extract_movies(ch_driver, franchises_df)
    data = extract_imdb(ch_driver, movies_df)
    data.loc[:, ['Franchise', 'Movie_title', 'Release_Year', 'IMDB_id']].to_csv("output.csv", index=False)
