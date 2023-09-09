import random
import string
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def config_chrome() -> webdriver.Chrome:
    extension_path = 'extension_10_25_0_0.crx'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_extension(extension_path)
    driver = webdriver.Chrome(options=chrome_options)
    extension_popup_url = f'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/popup.html'
    driver.get(extension_popup_url)
    driver.close()
    time.sleep(10)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    print('chrome drive config success')
    return driver


def config_chrome_test() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver: webdriver.Chrome, password: str) -> str:
    print('login process starts ... ')
    # print('step 1 done')
    driver.find_element(By.XPATH, '//button[@class="button btn--rounded btn-primary"]').click()
    time.sleep(2)
    # print('step 2 done')
    driver.find_element(By.XPATH, '//button[@class="button btn--rounded btn-primary btn--large"]').click()
    time.sleep(3)
    # print('step 3 done')
    driver.find_element(By.XPATH, '//input[@data-testid="create-password-new"]').send_keys(password)
    driver.find_element(By.XPATH, '//input[@data-testid="create-password-confirm"]').send_keys(password)
    driver.find_element(By.XPATH, '//input[@class="check-box far fa-square"]').click()
    time.sleep(2)
    # print('step 4 done')
    driver.find_element(By.XPATH, '//button[@data-testid="create-password-wallet"]').click()
    time.sleep(2)
    # print('step 5 done')
    driver.find_element(By.XPATH, '//button[@data-testid="secure-wallet-later"]').click()
    time.sleep(2)
    # print('step 6 done')
    driver.find_element(By.XPATH, '//input[@data-testid="skip-srp-backup-popover-checkbox"]').click()
    time.sleep(2)
    # print('step 7 done')
    driver.find_element(By.XPATH, '//button[@data-testid="skip-srp-backup"]').click()
    time.sleep(2)
    # print('step 8 done')
    driver.find_element(By.XPATH, '//button[@data-testid="onboarding-complete-done"]').click()
    time.sleep(2)
    # print('step 9 done')
    driver.find_element(By.XPATH, '//button[@data-testid="pin-extension-next"]').click()
    time.sleep(2)
    # print('step 10 done')
    driver.find_element(By.XPATH, '//button[@data-testid="pin-extension-done"]').click()
    time.sleep(2)
    # print('step 11 done')
    driver.find_element(By.XPATH, '//div[@class="selected-account__copy"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="account-options-menu-button"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@data-testid="account-options-menu__account-details"]').click()
    time.sleep(2)
    wallet = driver.find_element(By.XPATH, '//div[@class="qr-code__address"]').text
    time.sleep(2)
    print('login success')
    return wallet
    # //button[@class="mm-box mm-text mm-button-base mm-button-base--size-md whats-new-popup__button mm-button-primary mm-text--body-md-medium mm-box--padding-right-4 mm-box--padding-left-4 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-inverse mm-box--background-color-primary-default mm-box--rounded-pill"]


def alphanomics(driver: webdriver.Chrome) -> str:
    print('alphanomics site access starts....')
    driver.get('https://platform.alphanomics.io/access?ref_code=tw&next=/wallet-search')
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@class="btn-connect"]').click()
    time.sleep(5)

    shadow_host_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="dynamic-modal-shadow"]')
    # Execute JavaScript code to interact with elements inside the Shadow DOM
    script = """
        const shadowDomElement = arguments[0].shadowRoot;
        const imgElement = shadowDomElement.querySelector('img[data-testid="wallet-icon-MetaMask"]');
        imgElement.click();
    """
    driver.execute_script(script, shadow_host_element)
    main_page = driver.current_window_handle
    time.sleep(5)

    for handle in driver.window_handles:
        if handle != main_page:
            login_page = handle

    # change the control to signin page
    driver.switch_to.window(login_page)
    time.sleep(5)

    print('move the driver to meta mask connect pop up')
    driver.find_element(By.XPATH, '//button[@class="button btn--rounded btn-primary"]').click()
    time.sleep(2)
    # print('step 1 done')
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.find_element(By.XPATH, '//button[@data-testid="page-container-footer-next"]').click()
    time.sleep(5)
    # print('step 2 done')
    driver.find_element(By.XPATH, '//button[@data-testid="request-signature__sign"]').click()
    time.sleep(5)
    print("meta mask connect done, move back")
    driver.switch_to.window(main_page)
    time.sleep(5)
    shadow_host_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="dynamic-modal-shadow"]')
    script = """
        const shadowDomElement = arguments[0].shadowRoot;
        const imgElement = shadowDomElement.querySelector('button[class="button button--expanded button--padding-large button--primary button--rounded "]');
        imgElement.click();
    """
    driver.execute_script(script, shadow_host_element)
    time.sleep(5)
    driver.get('https://platform.alphanomics.io/profile')
    time.sleep(5)
    invite_link = driver.find_element(By.XPATH, '//input[@class="invite-link"]').get_attribute('value')
    return invite_link


def run():
    print('Script starts running ...')
    driver = config_chrome()
    characters = string.ascii_letters + string.digits
    random_password = ''.join(random.choice(characters) for _ in range(8))
    wallet = login(driver, random_password)
    time.sleep(3)
    invite_link = alphanomics(driver)
    print('---------------------------------------------------')
    print('New Account have been created')
    print(f'account name = Account 1, password = {random_password}, wallet = {wallet}')
    print(f'Your invitation link = {invite_link}')


if __name__ == '__main__':
    run()
