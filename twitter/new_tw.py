import csv
import datetime
import logging
import math
import random
import subprocess
import time

import twAuto
from dateutil import parser
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# install dependencies
subprocess.check_call(['pip', 'install', 'python-dateutil'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'twAuto'])

# define twitter credentials
TWITTER_EMAIL = 'khaledibnmahbub@gmail.com'
TWITTER_USERNAME = 'KhaledIbnMahbu1'
TWITTER_PASSWORD = 'Allahhelpme6832'

# define the keywords, for best result named it like as the company page name
KEYWORDS = ['Burger King']
START_DATE = '2022-01-01'  # format should be (YYYY-mm-dd)
END_DATE = '2022-12-31'    # format should be (YYYY-mm-dd)

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def login_via_tw_auto():
    tw = twAuto.twAuto(
        username=TWITTER_USERNAME,
        email=TWITTER_EMAIL,
        password=TWITTER_PASSWORD,
        chromeDriverMode="auto",
        pathType="xPath",
        headless=True  # Headless must be False to use this function.
    )

    tw.start()
    # tw.manualCookieCreation()
    tw.login()
    return tw.driver


def wait_until_find_element(driver, selector, param):
    start_time = time.time()
    while True:
        try:
            driver.find_element(selector, param)
            break
        except Exception as e:
            if math.ceil(time.time() - start_time) > 10:
                break
            continue


def scroll_down_page(driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    html = driver.find_element(By.TAG_NAME, 'html')
    for i in range(30):
        html.send_keys(Keys.ARROW_DOWN)
    time.sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")

    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def collect_all_tweets_from_current_view(driver, lookback_limit=25):
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]')))
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(driver, parent, child, card, search_key):
    try:
        user = card.find_element(By.XPATH, './/span').text.strip()
    except Exception as exx:
        user = ""

    try:
        handle = 'https://twitter.com/' + card.find_element(By.XPATH, './/span[contains(text(), "@")]').text.strip()
    except Exception as exx:
        handle = ""

    try:
        postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime').strip()
    except Exception as exx:
        postdate = ''

    try:
        responding = card.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text.strip()
    except Exception as exx:
        responding = ''

    try:
        reply_count = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text.strip()
    except Exception as exx:
        reply_count = ""
    try:
        retweet_count = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text.strip()
    except Exception as exx:
        retweet_count = ""

    try:
        like_count = card.find_element(By.XPATH, './/div[@data-testid="like"]').text.strip()
    except Exception as exx:
        like_count = ""

    try:
        tweet_website = card.find_element(By.XPATH, './/div[2]/div/div[3]/a').get_attribute('href').strip()
    except Exception as exx:
        tweet_website = ""

    try:
        # driver.save_screenshot("image.png")
        view_count = card.find_element(By.XPATH, './/div[4]/a/div/div[2]/span/span/span').text
    except Exception as exx:
        view_count = ""

    images_to_link = ''
    try:
        images = card.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']//img")
        for image in images:
            images_to_link += f"{image.get_attribute('src').strip()}, "
    except Exception as exx:
        pass

    videos_to_link = ''
    try:
        videos = card.find_elements(By.XPATH, '//div[@data-testid="videoPlayer"]//video')
        for video in videos:
            videos_to_link += f"{video.get_attribute('src').strip()}, "
    except Exception as exx:
        pass

    try:
        company_replay = ''
        driver.switch_to.window(child)
        time.sleep(1)
        driver.get(tweet_website)
        wait_until_find_element(driver, By.XPATH, '//article[@data-testid="tweet"]')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        replies = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        for replay in replies:
            try:
                replay_user = replay.find_element(By.XPATH, './/span').text.strip()
                if search_key not in replay_user:
                    continue
                company_replay = replay.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text.strip()
                if search_key in replay_user:
                    break
            except Exception as ex:
                continue

        driver.switch_to.window(parent)
        time.sleep(1)
    except Exception as exx:
        company_replay = ""

    if reply_count == '':
        reply_count = "0"
    if retweet_count == '':
        retweet_count = "0"
    if like_count == '':
        like_count = "0"
    if view_count == '':
        view_count = "N/A"

    return ['Post&Comment', search_key, tweet_website, user, handle, postdate, responding, images_to_link,
            videos_to_link, 'False', company_replay, str(reply_count), str(retweet_count), str(like_count),
            str(view_count)]


def create_csv(f_name: str):
    with open(f'{f_name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Category", "Keyword", "Tweet_Website", "Author_Name", "Author_Web_Page_URL", "Tweet_Timestamp",
                 "Tweet_Content", "Tweet_Image_URL", "Tweet_Video_URL", "Tweet_AD", "Company_Reply",
                 "Tweet_Number_of_Reviews", "Tweet_Number_of_Retweets", "Tweet_Number_of_Likes",
                 "Tweet_Number_of_Looks"]
        writer.writerow(field)
    logging.info(f'created a new csv file named `{f_name}`')


def write_csv(f_name: str, row: list):
    with open(f'{f_name}.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def check_duplicate(rows: list, row: list) -> bool:
    for item in rows:
        if item[3] == row[3] and item[5] == row[5]:
            return True
    return False


def scrapper(f_name, keywords):
    driver = login_via_tw_auto()
    parent = driver.window_handles[0]
    driver.execute_script("window.open('');")
    time.sleep(1)
    child = driver.window_handles[1]
    driver.switch_to.window(parent)
    time.sleep(1)

    counter = 0
    for keyword in keywords:
        since_date = parser.parse(START_DATE).date()
        until_date = since_date + datetime.timedelta(days=1)
        while str(since_date) != END_DATE:
            added_rows = []
            search = f'https://twitter.com/search?q={keyword}%20until%3A{until_date}%20since%3A{since_date}&src=typed_query'
            driver.get(search)
            time.sleep(2)
            last_position = None
            end_of_scroll_region = False
            while not end_of_scroll_region:
                last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
                cards = collect_all_tweets_from_current_view(driver)
                for card in cards:
                    try:
                        new_row = extract_data_from_current_tweet_card(driver, parent, child, card, keyword)
                        if new_row[4] != '' and check_duplicate(added_rows, new_row) is False:
                            write_csv(f_name, new_row)
                            logging.info(f'--> {counter + 1}. new entry added for keyword={keyword}, date={since_date}')
                            counter += 1
                            added_rows.append(new_row)

                    except Exception as ex:
                        continue

            since_date = until_date
            until_date = until_date + datetime.timedelta(days=1)


if __name__ == '__main__':
    logging.info('Script start running ...')
    file_name = f'data_{random.randint(1, 9999)}'
    create_csv(file_name)
    scrapper(file_name, KEYWORDS)
    logging.info(f'Script successfully executed & saved data at `{file_name}.csv`')
