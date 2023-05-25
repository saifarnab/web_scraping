import csv
import datetime
import random
import subprocess
import time
import pyperclip

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# define variables
STREAMY_USER_ID = 'temp123'
STREAMY_USER_PASS = '%$OV^@Kxc!44s3ez)KWQy#Kk'
TELEGRAM_TOKEN = '6082996789:AAHGb1brvQfJzjrHy9H4WsCw-QRmESXXq7M'
TELEGRAM_CHANNEL_ID = '10016402776821'


# install dependencies
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'requests'])
subprocess.check_call(['pip', 'install', 'pyperclip'])


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)


def csv_file_init(file_name: str):
    try:
        with open(file_name, 'x', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(["LastPushedId"])
            print('File created successfully.')
    except FileExistsError:
        pass


def get_last_telegram_id(file_name: str):
    try:
        df = pd.read_csv(file_name, sep=';')
        return df['LastPushedId'][0]
    except Exception as e:
        return None


def write_csv(file_name: str, message_id: int):
    try:
        df = pd.read_csv(file_name)
        df.loc[0, 'LastPushedId'] = str(message_id)
        df.to_csv(file_name, index=False)
    except Exception as e:
        print(e)


def streamy_login(driver) -> bool:
    try:
        driver.get('https://streamyme.com/wp-login.php')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'user_login')))
        driver.find_element(By.ID, 'user_login').send_keys(STREAMY_USER_ID)
        driver.find_element(By.ID, 'user_pass').send_keys(STREAMY_USER_PASS)
        time.sleep(1)
        driver.find_element(By.ID, 'wp-submit').click()
        while driver.current_url != 'https://streamyme.com/wp-admin/':
            continue
        time.sleep(1)
        return True

    except Exception as e:
        return False


def new_post(driver, title, content) -> bool:
    try:
        driver.get('https://streamyme.com/wp-admin/post-new.php')

        # title
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'title')))
        driver.find_element(By.ID, 'title').send_keys(title)

        # content
        driver.find_element(By.ID, 'content-tmce').click()
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'content_ifr')))
        iframe = driver.find_element(By.ID, 'content_ifr')
        driver.switch_to.frame(iframe)
        time.sleep(1)

        pyperclip.copy(content)
        element = driver.find_element(By.XPATH, '//body[@id="tinymce"]')
        element.send_keys(Keys.CONTROL, 'v')

        # content = str(content).replace("'", "\\'")
        # element = driver.find_element(By.XPATH, '//body[@id="tinymce"]')
        # driver.execute_script("arguments[0].innerHTML = '{}'".format(content), element)
        # element.send_keys('.')
        # element.send_keys(Keys.BACKSPACE)

        time.sleep(1)
        driver.switch_to.default_content()
        time.sleep(1)

        # category
        driver.find_element(By.ID, 'in-category-175').click()
        time.sleep(1)

        # publish
        while True:
            try:
                WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//input[@class="button button-primary button-large"]')))
                driver.find_element(By.ID, 'publish').click()
                time.sleep(5)
                break
            except Exception as e:
                continue

        return True
    except Exception as e:
        print(e)
        return False


def get_channel_messages() -> list:
    try:
        api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"chat_id": TELEGRAM_CHANNEL_ID}
        response = requests.get(api_url, params=params)
        data = response.json()

        if response.status_code == 200 and data["ok"]:
            return data["result"]
        else:
            print("Failed to retrieve channel messages.")
            return []
    except Exception as e:
        return []


def get_current_datetime():
    return datetime.datetime.now().strftime("%d.%m.%Y / %H:%M")


def waiting_time():
    temp = random.randint(2, 4) * 60
    print(f'No new post to publish. Wait {temp} seconds for next try.')
    time.sleep(temp)


def scrapper():
    print('Script starts running ...')
    file_name = 'last_telegram_id_pointer.csv'

    while True:
        # create csv if not created
        csv_file_init(file_name)

        # get telegram recent posts
        messages = get_channel_messages()
        messages.reverse()

        if len(messages) < 1:
            print('Not new post available in the channel')
            waiting_time()

        # get last publish telegram id
        last_telegram_id = 0 if get_last_telegram_id(file_name) is None else get_last_telegram_id(file_name)
        new_last_telegram_id = last_telegram_id

        # config driver
        driver = config_driver()

        # login to WordPress
        if streamy_login(driver) is False:
            print('Failed to login')
            continue

        # publish new post
        for message in messages:
            update_id = message['update_id']
            if update_id > last_telegram_id:
                try:
                    content = message['channel_post']['text']
                    title = f'Update - {get_current_datetime()}'
                    if new_post(driver, title, content) is True:
                        if update_id > new_last_telegram_id:
                            new_last_telegram_id = update_id
                        print(f'--> new post published.')
                except Exception as e:
                    continue

        write_csv(file_name, new_last_telegram_id)
        driver.close()
        waiting_time()


if __name__ == "__main__":
    scrapper()
