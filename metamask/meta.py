import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


def config_chrome() -> webdriver.Chrome:
    extension_path = 'extension_10_35_1_0.crx'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_extension(extension_path)
    driver = webdriver.Chrome(options=chrome_options)
    extension_popup_url = f'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/popup.html'
    driver.get(extension_popup_url)
    driver.close()
    time.sleep(10)
    driver.switch_to.window(driver.window_handles[0])
    return driver


def login(driver: webdriver.Chrome):
    driver.find_element(By.ID, 'onboarding__terms-checkbox').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@class="button btn--rounded btn-primary"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@class="button btn--rounded btn-primary btn--large"]').click()
    time.sleep(3)
    driver.find_element(By.XPATH, '//input[@data-testid="create-password-new"]').send_keys('1qazxsw2')
    driver.find_element(By.XPATH, '//input[@data-testid="create-password-confirm"]').send_keys('1qazxsw2')
    driver.find_element(By.XPATH, '//input[@class="check-box far fa-square"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="create-password-wallet"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="secure-wallet-later"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//input[@data-testid="skip-srp-backup-popover-checkbox"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="skip-srp-backup"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="onboarding-complete-done"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="pin-extension-next"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="pin-extension-done"]').click()
    time.sleep(2)
    # //button[@class="mm-box mm-text mm-button-base mm-button-base--size-md whats-new-popup__button mm-button-primary mm-text--body-md-medium mm-box--padding-right-4 mm-box--padding-left-4 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-inverse mm-box--background-color-primary-default mm-box--rounded-pill"]


def alphanomics(driver: webdriver.Chrome):
    # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
    # time.sleep(2)
    # driver.switch_to.window(driver.window_handles[1])
    # time.sleep(1)
    driver.get('https://platform.alphanomics.io/access?ref_code=tw&next=/wallet-search')
    time.sleep(3)
    driver.find_element(By.XPATH, '//button[@class="btn-connect"]').click()


def run():
    driver = config_chrome()
    # login(driver)
    time.sleep(3)
    alphanomics(driver)
    time.sleep(5000)


if __name__ == '__main__':
    run()
