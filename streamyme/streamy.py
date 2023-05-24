import csv
import subprocess
import sys
import time

import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent

# define variables
TELEGRAM_TOKEN = '6082996789:AAHGb1brvQfJzjrHy9H4WsCw-QRmESXXq7M'
TELEGRAM_ID = '10016402776821'

# install dependencies
# subprocess.check_call(['pip', 'install', 'user_agent'])
# subprocess.check_call(['pip', 'install', 'selenium'])
# subprocess.check_call(['pip', 'install', 'fake_useragent'])


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    return webdriver.Chrome(options=chrome_options)


def streamy_login(driver):
    driver.get('https://streamyme.com/wp-login.php')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#user_login')))
    driver.find_element(By.CSS_SELECTOR, '#user_login').send_keys('temp123')
    driver.find_element(By.CSS_SELECTOR, '#user_pass').send_keys('%$OV^@Kxc!44s3ez)KWQy#Kk')
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#wp-submit').click()
    while driver.current_url != 'https://streamyme.com/wp-admin/':
        continue
    time.sleep(1)


def new_post(driver, title, content):
    driver.get('https://streamyme.com/wp-admin/post-new.php')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#title')))
    driver.find_element(By.CSS_SELECTOR, '#title').send_keys(title)
    driver.find_element(By.CSS_SELECTOR, '#content-html').click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, '#content').send_keys(content)
    # driver.find_element(By.CSS_SELECTOR, '#publish').click()
    time.sleep(10000)


def get_channel_messages(token, channel_id):
    api_url = f"https://api.telegram.org/bot{token}/"
    method = "getUpdates"  # Retrieves recent messages
    params = {"chat_id": channel_id, "limit": 100}

    response = requests.get(api_url + method, params=params)
    data = response.json()

    if response.status_code == 200 and data["ok"]:
        messages = data["result"]
        return messages
    else:
        print("Failed to retrieve channel messages.")
        return []


def scrapper():
    driver = config_driver()
    streamy_login(driver)
    text = """
    Hey everyone!  Good morning! Just wanted to give you all a quick update on the current situation. Our amazing team has been working tirelessly throughout the night to bring back all the live channels, and I’m happy to report that we now have 60% of them back online.  The remaining channels will be restored gradually throughout the day.

Now, I know some of you might be wondering about the VOD section. Unfortunately, it’s not functioning at the moment.  Our first priority is to recover all the live channels, and once that’s done, we’ll start rebuilding the VOD section. Just a reminder, the entire data center where our data was stored had to be closed down, so we’re essentially starting from scratch and taking it one step at a time.

A few customers have asked if any personal data was compromised during this process. I want to assure everyone that no personal data has been captured by the Netherlands task force or anyone else. The data center only stored the VOD section and managed the traffic for the live channels. So, there’s no need to worry about your personal information. Also, please note that we don’t store any personal user info except for email addresses and subscription lengths.  We take your privacy seriously, and that information is securely encrypted on a private server. No one can access your emails and subscription length info.

We sincerely apologize for the inconvenience caused by the current service disruptions. To make it up to you, we’ll be adding 7 extra days to all subscriptions as compensation for the trouble. We truly appreciate your patience and understanding as we work hard to bring the service back to its full glory. 

Wishing you all an awesome day ahead! 

the data should be presented in a nice and professional way, so customers easily can see the newest posts at the top, and then see older news under that
    """
    new_post(driver, 'Update – 24.05.2023', text)


if __name__ == "__main__":
    # scrapper()
    # Replace with your Telegram token and channel ID
    telegram_token = TELEGRAM_TOKEN
    channel_id = TELEGRAM_ID

    messages = get_channel_messages(telegram_token, channel_id)
    print(len(messages))

    for message in messages:
        print('------------------------')
        print(message)

