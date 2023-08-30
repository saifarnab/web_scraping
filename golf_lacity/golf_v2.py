import csv
import os
import time

from datetime import datetime, timedelta

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# urls (Do not touch)
LOGIN_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/login"
SEARCH_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/search"

# Credentials & Configurations
DRIVER_PATH = "chromedriver"
TRACKER = 'tracker.csv'
BOOKING_DAYS = ['Thursday', 'Friday', 'Wednesday']
WAITING_TIME = 5  # seconds
USERNAME = "la-165095"
PASSWORD = "Snowing23#"
TIMER = "9:00 AM–7:00 PM"
DAYS_IN_ADVANCE = 9


def config_driver() -> webdriver.Chrome:
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 "
                  "Safari/537.36")
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
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
    chrome_options.add_argument(user_agent)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def config_uc_driver():
    version_main = int(chromedriver_autoinstaller.get_chrome_version().split(".")[0])
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    options = uc.ChromeOptions()
    options.add_argument(user_agent)
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    # options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options=options, headless=False, use_subprocess=False, driver_executable_path=DRIVER_PATH,
                       version_main=version_main)
    return driver


def convert_to_24hrs(time_str: str) -> str:
    try:
        # Parse the input time using the 12-hour format
        input_format = "%I:%M%p"
        output_format = "%H:%M"

        # Convert the time to 24-hour format
        converted_time = datetime.strptime(time_str, input_format).strftime(output_format)

        return converted_time
    except ValueError:
        return "Invalid input format"


def parse_timer(value: str) -> (int, int):
    timer = value.replace(" ", "").strip().upper().split("–")
    first_timer = int(float(convert_to_24hrs(timer[0]).replace(':', '.')))
    second_timer = int(float(convert_to_24hrs(timer[1]).replace(':', '.')))
    return abs(first_timer - 5) * 2 - 1, abs(second_timer - 19) * 2 - 2


def add_days(date_str: str) -> str:
    start_date = datetime.strptime(date_str, "%m/%d/%Y")
    new_date = start_date + timedelta(days=DAYS_IN_ADVANCE)
    return new_date.date().strftime("%m/%d/%Y")


def is_valid_time(input_time: str) -> bool:
    try:
        timer = TIMER.upper().replace(" ", "").split('–')
        parsed_time = datetime.strptime(input_time.replace(" ", "").strip(), '%I:%M%p')

        start_time = datetime.strptime(timer[0].strip(), '%I:%M%p')
        end_time = datetime.strptime(timer[1].strip(), '%I:%M%p')
        if start_time <= parsed_time <= end_time:
            return True
        else:
            return False

    except ValueError as ve:
        return False


def create_tracker():
    columns = ["TeeDate"]
    if os.path.exists(TRACKER):
        return
    with open(TRACKER, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
    print(f'{TRACKER} is created.')


def add_data_to_csv(data):
    with open(TRACKER, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data])


def is_data_in_csv(target_data) -> bool:
    with open(TRACKER, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[0] == target_data:
                return True
    return False


def is_booking_eligible() -> bool:
    date_object = datetime.now().date()
    day_name = date_object.strftime("%A")
    if day_name not in BOOKING_DAYS:
        return False
    key = f"{date_object.strftime('%d|%m|%y')}|{day_name}"
    if is_data_in_csv(key) is True:
        return False
    return True


def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(20)
    driver.save_screenshot('s1.png')
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter User Name']").send_keys(USERNAME)
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter Password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)


def search(driver):
    driver.get(SEARCH_URL)
    time.sleep(2)
    driver.save_screenshot('s2.png')
    time_date = driver.find_element(By.ID, 'pickerDate').get_attribute("value")
    driver.execute_script(f"document.getElementById('pickerDate').value = '{add_days(time_date)}'")
    time.sleep(1)
    driver.find_element(By.ID, 'pickerDate').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.save_screenshot('s3.png')
    driver.find_element(By.ID, 'pickerDate').send_keys(Keys.ESCAPE)
    time.sleep(1)
    element = driver.find_element(By.CSS_SELECTOR, '.search-clear-all')
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)
    driver.save_screenshot('s4.png')
    element = driver.find_element(By.XPATH, "//label[@id='courseLabel_Rancho Park']")
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)
    driver.save_screenshot('s5.png')

    first_timer, second_timer = parse_timer(TIMER)
    first_slider = driver.find_element(By.XPATH,
                                       "//div[@on-handle-up='ec.onTeeTimeFilterHandleUp()']//div[@class='ngrs-handle ngrs-handle-min']//i")
    second_slider = driver.find_element(By.XPATH,
                                        "//div[@on-handle-up='ec.onTeeTimeFilterHandleUp()']//div[@class='ngrs-handle ngrs-handle-max']//i")

    ActionChains(driver).drag_and_drop_by_offset(first_slider, 10 * first_timer, 200).perform()
    time.sleep(5)
    driver.save_screenshot('s6.png')
    ActionChains(driver).drag_and_drop_by_offset(second_slider, -10 * second_timer, 200).perform()
    time.sleep(5)
    driver.save_screenshot('s7.png')


def reservation(driver):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//li[1]//div[3]//button[1]')))
    except Exception as e:
        print('Not tee available at given time')
        exit()

    time.sleep(5)
    driver.find_element(By.XPATH, "//li[1]//div[3]//button[1]").click()
    time.sleep(5)
    driver.save_screenshot('s8.png')
    cart_time = driver.find_element(By.XPATH, "//strong[@data-ng-bind='ec.teeTimeDisplay']").text
    if is_valid_time(cart_time) is False:
        raise Exception('Invalid cart time')
    driver.find_element(By.ID, "addToCartBtn").click()
    time.sleep(5)
    driver.save_screenshot('s9.png')
    driver.find_element(By.CSS_SELECTOR, ".btn.btn-10.btn-default").click()
    time.sleep(5)
    driver.save_screenshot('s10.png')
    if 'payment' not in driver.current_url:
        print('You Have An Existing Reservation at the given time')
        quit()
    driver.find_element(By.CSS_SELECTOR, "#buyTeeTime").click()
    time.sleep(5)
    driver.save_screenshot('s11.png')
    # driver.find_element(By.CSS_SELECTOR, "#topFinishBtn").click()
    # time.sleep(2)
    # driver.save_screenshot('s12.png')
    date_object = datetime.now().date()
    day_name = date_object.strftime("%A")
    key = f"{date_object.strftime('%d|%m|%y')}|{day_name}"
    add_data_to_csv(key)


def run():
    while True:
        driver = None
        create_tracker()
        if is_booking_eligible() is False:
            print(f'Invalid booking time. After {WAITING_TIME} seconds it will retry')
            time.sleep(WAITING_TIME)
            continue
        print('Reservation process is starting ...')
        for i in range(5):
            try:
                driver = config_uc_driver()
                login(driver)
                print('Login completed!')
                search(driver)
                print('Searching completed!')
                reservation(driver)
                print('Reservation completed!')
                driver.close()
                break
            except Exception as ex:
                if driver is not None:
                    driver.close()
                print(ex)
                print("Failed to book the reservation process, rollback the program again.")
                time.sleep(2)
                continue


if __name__ == '__main__':
    run()
