import time
from datetime import datetime, timedelta

import undetected_chromedriver as uc
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# urls (Do not touch)
LOGIN_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/login"
SEARCH_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/search"

# Credentials & Configurations
DRIVER_PATH = "/home/dfs/Documents/web_scraping/golf_lacity/chromedriver"
USERNMAE = "la-165095"
PASSWORD = "Snowing23#"
TIMER = "9:00 AM–11:00 AM"
DAYS_IN_ADVANCE = 7


def config_uc_driver():
    return uc.Chrome(headless=True, use_subprocess=False, driver_executable_path=DRIVER_PATH)


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


def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter User Name']").send_keys(USERNMAE)
    driver.find_element(By.CSS_SELECTOR, "input[title='Enter Password']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)


def search(driver):
    driver.get(SEARCH_URL)
    time.sleep(2)
    time_date = driver.find_element(By.ID, 'pickerDate').get_attribute("value")
    driver.execute_script(f"document.getElementById('pickerDate').value = '{add_days(time_date)}'")
    time.sleep(1)
    driver.find_element(By.ID, 'pickerDate').send_keys(Keys.ENTER)
    time.sleep(2)
    driver.find_element(By.ID, 'pickerDate').send_keys(Keys.ESCAPE)
    time.sleep(1)
    element = driver.find_element(By.CSS_SELECTOR, '.search-clear-all')
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)
    element = driver.find_element(By.XPATH, "//label[@id='courseLabel_Rancho Park']")
    driver.execute_script("arguments[0].click()", element)
    time.sleep(1)

    first_timer, second_timer = parse_timer(TIMER)
    first_slider = driver.find_element(By.XPATH,
                                       "//div[@on-handle-up='ec.onTeeTimeFilterHandleUp()']//div[@class='ngrs-handle ngrs-handle-min']//i")
    second_slider = driver.find_element(By.XPATH,
                                        "//div[@on-handle-up='ec.onTeeTimeFilterHandleUp()']//div[@class='ngrs-handle ngrs-handle-max']//i")

    ActionChains(driver).drag_and_drop_by_offset(first_slider, 10 * first_timer, 200).perform()
    time.sleep(5)
    ActionChains(driver).drag_and_drop_by_offset(second_slider, -10 * second_timer, 200).perform()
    time.sleep(5)


def reservation(driver):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//li[1]//div[3]//button[1]')))
    except Exception as e:
        print('Not tee available at given time')
        exit()

    driver.find_element(By.XPATH, "//li[1]//div[3]//button[1]").click()
    time.sleep(2)
    driver.find_element(By.ID, "addToCartBtn").click()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, ".btn.btn-10.btn-default").click()
    time.sleep(5)
    if 'payment' not in driver.current_url:
        print('You Have An Existing Reservation at the given time')
        quit()
    driver.find_element(By.CSS_SELECTOR, "#buyTeeTime").click()
    time.sleep(5)
    driver.find_element(By.CSS_SELECTOR, "#topFinishBtn").click()
    time.sleep(2)


def run():
    print('Reservation process is starting ...')
    try:
        driver = config_uc_driver()
    except Exception as ex:
        print('Chrome is not responding, please run again.')
        exit()

    for i in range(5):
        try:
            login(driver)
            print('Login completed!')
            search(driver)
            print('Searching completed!')
            reservation(driver)
            print('Reservation completed!')
            break
        except Exception as ex:
            # print(ex)
            print("Failed to book the reservation process, rollback the program again.")
            continue


if __name__ == '__main__':
    run()
