import time

import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    return webdriver.Chrome(options=chrome_options)


def insert_row(new_data: list):
    df = pd.read_excel('sport.xlsx')
    new_row = {
        'Name': new_data[0],
        'E-Mail': new_data[1],
        'Sportart(en)1': new_data[2],
        'Sportart(en)2': new_data[3],
        'Sportart(en)3': new_data[4],
        'Sportart(en)4': new_data[5],
        'Sportart(en)5': new_data[6],
        'Sportart(en)6': new_data[7],
        'Sportart(en)7': new_data[8],
        'Sportart(en)8': new_data[9],
        'Sportart(en)9': new_data[10],
        'Sportart(en)10': new_data[11],
        'Sportart(en)11': new_data[12],
    }
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_excel('sport.xlsx', index=False)


def scrapper():
    print('Script starts ...')
    driver = config_driver()
    driver.get('https://vereinssuche.thueringen-sport.de/')
    ort = driver.find_element(By.ID, 'dataForm:orgaOrt')
    ort.send_keys('Erfurt')
    driver.find_element(By.XPATH, '//button[@id="dataForm:j_idt75"]').click()
    time.sleep(10)
    for i in range(306):
        try:
            dbx = '//tr//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"]'
            details_buttons = driver.find_elements(By.XPATH, dbx)
            print(f'Seite = {i + 1}')
            for details_button in details_buttons:
                try:
                    details_button.click()
                    time.sleep(8)
                    sport_name = driver.find_element(By.XPATH, "//div[@class='detailinfo h3']").text.strip()
                    email = driver.find_element(By.XPATH,
                                                '//body[1]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[2]/table[1]/tbody[1]/tr[2]/td[2]').text.strip()
                    sport = driver.find_element(By.XPATH,
                                                '//body[1]/div[1]/div[1]/div[1]/div[2]/form[1]/div[1]/div[3]/div[2]/table[1]/tbody[1]/tr[6]/td[2]').text
                    driver.find_element(By.CSS_SELECTOR,
                                        "button[id='detailForm:topCloseButton'] span[class='ui-button-text ui-c']").click()

                    sport = str(sport).replace('\n', ',').strip().split(',')
                    if len(sport) == 1:
                        data = [sport_name, email, sport[0].strip(), '', '', '', '', '', '', '', '', '', '']
                    elif len(sport) == 2:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), '', '', '', '', '', '', '', '',
                                '']
                    elif len(sport) == 3:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(), '', '', '', '',
                                '',
                                '', '', '']
                    elif len(sport) == 4:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                '', '', '', '', '', '', '']
                    elif len(sport) == 5:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), '', '', '', '', '', '']
                    elif len(sport) == 6:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), '', '', '', '', '']
                    elif len(sport) == 7:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), sport[6].strip(), '', '', '', '']
                    elif len(sport) == 8:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), sport[6].strip(), sport[7].strip(), '', '', '']
                    elif len(sport) == 9:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), sport[6].strip(), sport[7].strip(),
                                sport[8].strip(),
                                '', '']
                    elif len(sport) == 10:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), sport[6].strip(), sport[7].strip(),
                                sport[8].strip(),
                                sport[9].strip(), '']
                    else:
                        data = [sport_name, email, sport[0].strip(), sport[1].strip(), sport[2].strip(),
                                sport[3].strip(),
                                sport[4].strip(), sport[5].strip(), sport[6].strip(), sport[7].strip(),
                                sport[8].strip(),
                                sport[9].strip(), sport[10].strip()]

                    insert_row(data)
                    print(f'{sport_name} inserted. <{len(sport)}>')
                    time.sleep(1)
                except Exception as e:
                    print(e)

            driver.find_element(By.XPATH, "//span[@class='ui-icon ui-icon-seek-next']").click()
            time.sleep(2)
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    scrapper()
