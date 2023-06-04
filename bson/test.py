import undetected_chromedriver as uc


def config_uc_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    driver = uc.Chrome(options=chrome_options)
    v = driver.get('https://www.thuisbezorgd.nl/' + '1016')
    print(v)


config_uc_driver()