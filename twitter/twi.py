import math
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from datetime import datetime, date
import calendar
import os
from time import sleep
import csv
from random import randint
import re
from googletrans import Translator


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


def get_month_range(year, month, day):
    start = date.today().replace(day=day).day
    _, end = calendar.monthrange(year, month)
    # print((start,end))
    d = []
    for mon in range(start, end):
        d.append((mon, mon + 1))
    return d


def wait_until_find_element(driver, selector, param):
    start_time = time.time()
    while True:
        try:
            driver.find_element(selector, param)
            break
        except Exception as e:
            if math.ceil(time.time() - start_time) > 15:
                break
            continue


def handle_login():
    driver.get('https://twitter.com/i/flow/login')
    wait_until_find_element(driver, By.XPATH, '//input[@autocomplete="username"]')
    driver.find_element(By.XPATH, '//input[@autocomplete="username"]').send_keys('Imty94074113')
    next_buttons = driver.find_elements(By.XPATH,
                                        '//div[@class="css-901oao r-1awozwy r-6koalj r-18u37iz r-16y2uox r-37j5jr r-a023e6 r-b88u0q r-1777fci r-rjixqe r-bcqeeo r-q4m81j r-qvutc0"]')
    next_buttons[-2].click()
    wait_until_find_element(driver, By.XPATH, '//input[@autocomplete="current-password"]')
    driver.find_element(By.XPATH, '//input[@autocomplete="current-password"]').send_keys('W78$@gtr$hsdifsdfb')
    log_in = driver.find_elements(By.XPATH,
                                  '//div[@class="css-901oao r-1awozwy r-6koalj r-18u37iz r-16y2uox r-37j5jr r-a023e6 r-b88u0q r-1777fci r-rjixqe r-bcqeeo r-q4m81j r-qvutc0"]')
    log_in[-1].click()
    # wait_until_find_element(driver, By.XPATH, '//input[@aria-activedescendant="typeaheadFocus-0.6761253994815084"]')
    time.sleep(3)
    return True


def find_search_input_and_enter_criteria(search_term, driver):
    wait = WebDriverWait(driver, 20)
    xpath_search = '//input[@aria-label="Search query"]'
    sleep(3)

    # search_input = driver.find_element_by_xpath(xpath_search)
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, xpath_search)))
    # try:
    #     driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div[2]/div[2]/div/div/div/form/div[1]/div/div/label/div[2]/div').clear()
    # except:
    #     pas
    # try:
    search_input.send_keys(Keys.CONTROL + 'a' + Keys.CLEAR)
    # search_input.send_keys(Keys.CLEAR)
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    sleep(2)
    return True


def change_page_sort(tab_name, driver):
    wait = WebDriverWait(driver, 20)
    # tab = driver.find_element_by_link_text(tab_name)
    tab = wait.until(EC.presence_of_element_located((By.LINK_TEXT, tab_name)))
    tab.click()
    xpath_tab_state = f'//a[contains(text(),\"{tab_name}\") and @aria-selected=\"true\"]'


def generate_tweet_id(tweet):
    return ''.join(tweet)


def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    html = driver.find_element(By.TAG_NAME, 'html')
    for i in range(30):
        html.send_keys(Keys.ARROW_DOWN)
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")

    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def save_tweet_data_to_csv(records, filepath, mode='a+'):
    # header = ['User', 'Handle', 'PostDate','Link To Image', 'TweetText', 'ReplyCount', 'RetweetCount', 'LikeCount']
    header = ['user', 'Extraction Of Date', 'Time', 'Content of Tweet', 'Link To Image', 'Number of Likes',
              'Number of Comments', 'Number of Retweet', 'Tweet Time', 'Post Date']
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            writer.writerow(records)


def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    wait = WebDriverWait(driver, 20)
    # page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    # sleep(1)
    wait.until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card):
    try:
        user = card.find_element_by_xpath('.//span').text

    except exceptions.NoSuchElementException:
        user = ""
    except exceptions.StaleElementReferenceException:
        return
    try:
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except exceptions.NoSuchElementException:
        handle = ""
    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        return
    try:
        link_to_image = card.find_element_by_xpath(
            ".//div/div/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/a").get_attribute('href')
    except exceptions.NoSuchElementException:
        link_to_image = ""

    try:
        # _comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
        _comment = card.find_element(By.XPATH, './div/div/div/div[2]/div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        _comment = ""
    try:
        _responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        _responding = ""
    # tweet_text = _comment + _responding
    tweet_text = _comment
    translator = Translator()
    result = translator.translate(tweet_text, dest='it')
    tweet_text = result.text
    try:
        reply_count = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    except exceptions.NoSuchElementException:
        reply_count = ""
    try:
        retweet_count = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except exceptions.NoSuchElementException:
        retweet_count = ""
    try:
        like_count = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    except exceptions.NoSuchElementException:
        like_count = ""
    images_to_link = []
    try:
        images = card.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']//img")
        for image in images:
            images_to_link.append(image.get_attribute('src'))
    except exceptions.NoSuchElementException:
        pass

    extraction_date = str(datetime.now().date())
    extraction_time = str(datetime.now().time())
    tweet_time = re.findall('\d\d:\d\d:\d\d', postdate)[0]
    post_date = postdate.split(',')[0].split('T')[0]
    # header = ['Extraction Of Date', 'Time', 'Cont ent of Tweet', 'Link To Image', 'Number of Likes',
    #           'Number of Comments', 'Number of Retweet', 'Tweet Time']
    # tweet = (user, handle, postdate,link_to_image, tweet_text, reply_count, retweet_count, like_count)
    images_to_link = ','.join(images_to_link)
    # print("{} : {}".format(len(images_to_link),images_to_link))

    first = (user, extraction_date, extraction_time)

    tweet = (tweet_text, images_to_link, like_count, reply_count, retweet_count, tweet_time, post_date)
    return first, tweet


def main(driver, username, password, search_term, filepath, day_m, month_m, page_sort='Latest'):
    last_position = None

    # unique_tweets = set()
    # '"Biodiversity" until:2018-12-25 since:2018-01-01'
    years = [2022]
    for year in years:
        filepath = f'./{term}/{year}.csv'
        save_tweet_data_to_csv(None, filepath, 'a')
        for month in range(month_m, 13):
            unique_tweets = set()
            days = get_month_range(year, month, day_m)
            day_m = 1
            # days.append((31,1))
            for start, end in days:
                # if start == 31:
                #     month = 12
                #     year = year - 1
                # Aceite de oliva "Aceite de oliva" until:2019-06-04 since:2019-06-03
                search_word = '{} "{}" until:{}-{}-{} since:{}-{}-{}'.format(search_term, search_term, year, month, end,
                                                                             year, month, start)
                # search_word = '"{}" until:{}-12-31 since:{}-01-01'.format(search_term,year,year)
                print('searching:', search_word)
                search_found = find_search_input_and_enter_criteria(search_word, driver)
                if not search_found:
                    return
                # print('did')
                # change_page_sort(page_sort, driver)
                sleep(3)
                last_position = None
                end_of_scroll_region = False
                print('hit 1')
                while not end_of_scroll_region:
                    cards = collect_all_tweets_from_current_view(driver)
                    # print(len(cards))
                    for card in cards:
                        try:
                            first, tweet = extract_data_from_current_tweet_card(card)
                        except:
                            continue
                        if not tweet:
                            continue

                        tweet_id = generate_tweet_id(tweet)
                        if tweet_id not in unique_tweets:
                            # pdt = post_date.split('/')[0]
                            # if not int(pdt) == end:
                            unique_tweets.add(tweet_id)
                            tweet = first + tweet
                            save_tweet_data_to_csv(tweet, filepath)
                        print('hit 2')
                        break
                    last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
                    print('hit 3')
                    break
                sleep(randint(6, 13))
                print('hit 4')
                break
            print('hit 5')
            break
        month_m = 1
        break
    # driver.quit()


if __name__ == '__main__':
    day_inp = int(input('Day: '))
    month_inp = int(input('month: '))
    usr = "Imty94074113"
    pwd = "W78$@gtr$hsdifsdfb"
    driver = get_driver(False)
    logged_in = handle_login()
    time.sleep(10)
    if not logged_in:
        print('something went wrong. please try again..')
    else:
        print('Logged in')
        terms = ['Burger King']
        for term in terms:
            try:
                os.mkdir(term)
            except:
                pass

            path = term + '.csv'
            # save_tweet_data_to_csv(None, path, 'a')
            main(driver, usr, pwd, term, path, day_inp, month_inp)
            sleep(randint(3, 7))
            break
