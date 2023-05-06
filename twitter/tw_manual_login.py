import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def config_driver() -> webdriver.Chrome:
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def handle_login(driver):
    try:
        driver.get('https://twitter.com/i/flow/login')
        while 'home' not in driver.current_url:
            continue
        time.sleep(2)
        return True
    except Exception as exx:
        return False


def scanner():
    driver = config_driver()
    while True:
        if handle_login(driver) is True:
            break
        logging.error('login failed, retrying...')
    logging.info('logging success.')


if __name__ == '__main__':
    logging.info('Script start running ...')
    scanner()
    logging.info(f'Script successfully executed!')
