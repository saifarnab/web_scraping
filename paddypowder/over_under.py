from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException

from bs4 import BeautifulSoup
from time import sleep
from random import randint
from datetime import datetime,timedelta

import os
import requests

def get_driver(headless: bool):
    options = webdriver.ChromeOptions()
    if headless is True:
        options.add_argument("--headless")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("lang=en-GB")
    options.add_argument('--ignore-certificate-errors')
    # self.options.add_argument('--lang=en')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    # self.options.add_argument("--log-level=OFF")
    options.add_argument("--log-level=3")

    path = os.path.join(os.getcwd(), 'chromedriver.exe')
    driver = webdriver.Chrome(path, options=options)
    return driver


def converting_min_hour_to_day(string):
    if 'Starting at' in string:
        t = string.split(' ')[2:]
        day = "Today - " + ' '.join(t)
        return day
    if 'Starting in' in string:
        t = string.split(' ')[-2]
        t = datetime.strptime(t, '%M')
        d = datetime.now()
        delta = timedelta(hours=d.hour, minutes=d.minute) + t
        day = 'Today - ' + delta.strftime('%H:%M')
        return day
    if 'Second' in string:
        t = string.split(' ')[-2]
        t = datetime.strptime(t, '%S')
        d = datetime.now()
        delta = timedelta(hours=d.hour, minutes=d.minute) + t
        day = 'Today - ' + delta.strftime('%H:%M')
        return day


def count_down(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end='\r')
        sleep(1)
        t -= 1

def get_weekday(day):
    # days  = ["mon","tue","wed","thu","fri","sat","sun"]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return days.index(day) + 1


def get_next_dayofweek_datetime(date_time, dayofweek):
    start_time_w = date_time.isoweekday()
    target_w = get_weekday(dayofweek)
    if start_time_w < target_w:
        day_diff = target_w - start_time_w
    else:
        day_diff = 7 - (start_time_w - target_w)

    return date_time + timedelta(days=day_diff)


def time_gmt(time: datetime):
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    gmt_time = time - timedelta(hours=5)
    day_name = days[gmt_time.weekday()]
    t = gmt_time.strftime('%H:%M')
    m_d = gmt_time.strftime('%d %b')
    gmt = "{} - {}".format(day_name, t)
    if gmt_time.weekday() == datetime.now().weekday():
        day_name = 'Today'
    gmt = "{} - {}  ({})".format(day_name, t, m_d)
    return gmt


def string_to_time(string):
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    # 'Starting in 10 minutes'
    # Tue 01:00
    # starting at 4:00
    # Thu 5 May 01:00
    string_c = string
    temp = string.split(' ')
    if len(temp) == 2:
        if temp[0] == 'Today':
            today = days[datetime.now().weekday()]
            today = datetime.strptime(temp[1], '%H:%M')
            today = datetime(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                             hour=today.hour, minute=today.minute)
            return today
        else:
            t = datetime.strptime(temp[1], '%H:%M')
            now_ind = datetime.now().weekday()
            # print(now_ind)
            date_ind = days.index(temp[0])
            compare = int(date_ind) - now_ind
            start_date = datetime.now().date()
            d = get_next_dayofweek_datetime(start_date, temp[0])
            output = datetime(year=d.year, month=d.month, day=d.day, hour=t.hour, minute=t.minute)

            return output
    else:
        # Thu 5 May 01:00
        t = datetime.strptime(string_c, "%a %d %b %H:%M")
        d = datetime(year=datetime.now().year, month=t.month, day=t.day, hour=t.hour, minute=t.minute)
        return d


def open_page(driver):
    wait = WebDriverWait(driver, 20)
    driver.get('https://www.paddypower.com/search')
    while True:
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
            break
        except:
            pass



def search_keyword(driver, keyword) -> list:
    wait = WebDriverWait(driver, 20)
    driver.get('https://www.paddypower.com/search')
    sleep(1)
    while True:
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='search']")))
            break
        except:
            driver.get('https://www.paddypower.com/search')
            sleep(5)

    driver.find_element(By.XPATH, "//input[@type='search']").clear()
    driver.find_element(By.XPATH, "//input[@type='search']").send_keys(keyword)
    sleep(5)
    tag = driver.find_element(By.TAG_NAME, 'html')
    for _ in range(40):
        tag.send_keys(Keys.ARROW_DOWN)

    # elements = driver.find_elements(By.XPATH, "//*[@class='list__item']")
    elements = driver.find_elements(By.XPATH, "//*[contains(@class,'list__item')]")
    links = []
    for element in elements:
        match = element.find_element(By.XPATH, './/a//div//div/div').text
        ignore = ['Spanish La Liga', 'Major League Baseball']
        if match not in ignore:
            link = element.find_element(By.XPATH, './/a').get_attribute('href')
            links.append(link)
    return links


def get_match(driver:webdriver,url:str):
    driver.get(url)
    sleep(5)
    elements = driver.find_elements(By.XPATH, "//*[@class='avb-item__event-row']")
    links = []
    for element in elements:
        link = element.find_element(By.XPATH, './/a').get_attribute('href')
        links.append(link)
    return links


def get_data_2_5_cards(driver, url):
    # print(url)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(url)
    except:
        driver = get_driver(True)
        open_page(driver)
        return get_data_2_5_cards(driver, url)

    ad = 0
    while True:
        try:
            # wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
            paddyodd = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'#WhatOddsPaddy - Up to 9/1')]")))
            paddyodd.click()
            break
        except:
            sleep(3)
            # print('paddy error')
            ad += 1
            # print(ad)
            if ad == 3:
                break
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        tournament = soup.find(class_='ui-scoreboard-template__header__row').find('span').text.strip()
    except:
        tournament = ''
    try:
        teams = soup.find_all(class_='ui-scoreboard-template__middle__row')
        match = teams[0].find('span').text.strip() + ' V ' + teams[1].find('span').text.strip()
    except:
        match = ''
    try:
        time = soup.find(class_='ui-scoreboard-template__bottom__row').find('span').text.strip().replace('Starting at', 'Today - ').replace("'", ' Second').replace(',', '')
        # print('Actual Time', time)
        if 'Starting' in time or 'Second' in time:
            if 'Second' in time:
                temp = int(time.strip(' ')[-2])
                if temp>59:
                    temp = 59
                    time = time.split(' ')[:-2]
                    time = ' '.join(time) + " {} Second".format(temp)
            time = converting_min_hour_to_day(time)
        time = string_to_time(time)
        # time = time_in_gmt(time)
        time = time_gmt(time)
        # print('Gmt time: ', time)
    except:
        time = ''
    # print('{}\n {}\n {}'.format(tournament,match,time))
    # elements = driver.find_elements(By.XPATH, ".//*[@class='outright-item-list__item']")
    elements = soup.find_all(class_='outright-item-list__item')
    for element in elements:
        data = element.text.strip()
        if "Each team to have 2+ cards" in data:
            data = ' '.join([line.strip() for line in data.strip().splitlines() if line.strip()])
            data = data.split(' ')
            try:
                temp = round(eval(data[-1]),2)
            except:
                temp = data[-1]

            data.pop(-1)
            # data = ' '.join(data)+" : "+temp
            data = ' '.join(data)+ " : ( {} )".format(temp)
            # d = ' '.join(data) + " : ({})".format(temp)

            message = formatting_for_tele(time, tournament, match, data)
            sending_telegram(message)

def get_data_over_under(driver,url):
    # print(url)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(url)
    except:
        sleep(randint(2,4))
        driver= get_driver(True)
        open_page(driver)
        return get_data_over_under(driver,url)
    ad = 0
    while True:
        try:

            paddyodd = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Cards Over/Under 3.5')]")))
            paddyodd.click()
            break
        except:
            sleep(3)
            ad += 1
            if ad==3:
                break
    sleep(3)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        tournament = soup.find(class_='ui-scoreboard-template__header__row').find('span').text.strip()
    except:
        tournament = ''
    try:
        teams = soup.find_all(class_='ui-scoreboard-template__middle__row')
        match = teams[0].find('span').text.strip() + ' V ' + teams[1].find('span').text.strip()
    except:
        match = ''
    try:
        time = soup.find(class_='ui-scoreboard-template__bottom__row').find('span').text.strip().replace('Starting at', 'Today -').replace("'", ' Second').replace(',','-')
        # print('Actual Time', time)
        if 'Starting' in time or 'Second' in time:
            if 'Second' in time:
                temp = int(time.strip(' ')[-2])
                if temp>59:
                    temp = 59
                    time = time.split(' ')[:-2]
                    time = ' '.join(time) + " {} Second".format(temp)
            time = converting_min_hour_to_day(time)
        # time = string_to_time(time)
        # time = time_gmt(time)
        # print('Gmt time: ', time)
    except:
        time = ''
    # print('{}\n {}\n {}'.format(tournament, match, time))
    # elements = driver.find_elements(By.XPATH, ".//*[@class='outright-item-list__item']")
    elements = soup.find_all(class_='outright-item-list__item')
    # print(len(elements))

    title_elements = soup.find_all(class_='event-card--item')

    cnd = False
    text = ""
    for element in title_elements:
        try:
            title = element.find(class_='accordion__title').text.strip()
        except:
            title = ''
        try:
            data = element.find_all(class_='outright-item-list__item')
            # print(data)

            for u in data:
                d = u.text.strip()
                if "Over 3.5 Cards" in d and "Cards Over/Under 3.5" in title:
                    d = ' '.join([line.strip() for line in d.strip().splitlines() if line.strip()]).replace('Cards', '')
                    d = d.split(' ')
                    try:
                        temp = round(eval(d[-1]),3)+ 1
                        temp = round(temp,2)
                    except:
                        temp = d[-1]
                    if 'EVS' == temp:
                        temp = 2.0
                    d.pop(-1)
                    # d = ' '.join(d) + " : " + temp
                    d = ' '.join(d) + " : ({})".format(temp)
                    text +=d
                    cnd = True
                    # print(d)
                elif "Under 3.5 Cards" in d and "Cards Over/Under 3.5" in title:
                    d = ' '.join([line.strip() for line in d.strip().splitlines() if line.strip()]).replace('Cards', '')
                    d = d.split(' ')
                    try:
                        temp = round(eval(d[-1]),3) + 1
                        temp = round(temp,2)
                    except:
                        temp = d[-1]
                    if 'EVS' == temp:
                        temp = 2.0
                    d.pop(-1)
                    # d = ' '.join(d) + " : "+temp
                    d = ' '.join(d) + " : ({})".format(temp)
                    text +='\n'+d
                    cnd = True
                    # print(d)

        except:
            data = ''
    if cnd and len(text)>3:
        # print('message done')
        message = formatting_for_tele(time,tournament,match,text)
        sending_telegram(message)
        cnd = False


def formatting_for_tele(time, tournament, match, data):
    message = f"""
{time}
{tournament}
{match}
{data}
"""
    return message


def sending_telegram(message):
    # client chat id and token
    token = '5301294416:AAG9gfjUof_i-uHI7VUALMfj3mQ3QZghA44'
    chat_id = '-1001682908414'



    url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    while True:
        try:
            result = requests.get(url)
            break
        except:
            # print('sending error')
            sleep(1)
            pass


def main():
    unique_id = set()
    print('Getting Data.')
    while True:
        driver = get_driver(True)
        open_page(driver)
        keywords = ['Cards Over/Under 3.5']
        match_url = []
        for k in keywords:
            # print(k)
            sleep(1)
            urls = search_keyword(driver,k)
            # print(urls)
            for url in urls:
                temp = url.split('/')[-1].split('-')
                if 'v' in temp:
                    if url not in unique_id:
                        unique_id.add(url)
                        sleep(randint(2,5))
                        match_url.append(url)
                        if k == '2+ Cards':
                            get_data_2_5_cards(driver,url)
                            # sending_telegram(msg)
                        elif k == 'Cards Over/Under 3.5':
                            url = url+'?tab=cards'
                            get_data_over_under(driver,url)
        # sending_telegram('done with first time')
        count_down(180)

if __name__ == '__main__':
    main()