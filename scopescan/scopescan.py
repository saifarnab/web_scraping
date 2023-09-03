import datetime
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def config_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(options=chrome_options)


def login(driver: webdriver.Chrome):
    driver.get('https://www.scopescan.ai/vcWatch/Alameda%20Research?network=eth')
    driver.find_element(By.XPATH, '//div[@class="sc-jIkXHa cXEIBb"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@placeholder='Please enter a email']").send_keys("sgreypublishing@gmail.com")
    driver.find_element(By.XPATH, "//input[@placeholder='Please enter a password']").send_keys("pass1234")
    time.sleep(1)
    driver.find_element(By.XPATH, '//div[@class="sc-iAKWXU fXGeqG login-but isOk"]').click()
    time.sleep(2)
    popup = driver.find_elements(By.XPATH, '//span[@class="anticon anticon-close ant-modal-close-icon"]')
    popup[1].click()
    time.sleep(1)
    print('Login successful')


def create_entity():
    df = pd.DataFrame(columns=["entity"])
    df.to_csv('entity.csv', index=False)
    print('Entity file have been created')


def create_output_file():
    if os.path.exists("output.xlsx"):
        print('Output file already available.')
        return
    df = pd.DataFrame(columns=['Entity', 'Address', 'Tag', 'Connection'])
    df.to_excel('output.xlsx', index=False)
    print(f"Output file has been created.")


def insert_data_into_excel(data):
    df = pd.read_excel("output.xlsx")
    new_data = pd.DataFrame(data, columns=df.columns)
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("output.xlsx", index=False)
    print(f"{data[0]} has been inserted into the output file")


def is_duplicate(address: str) -> bool:
    excel_file = "output.xlsx"
    df = pd.read_excel(excel_file)
    if address in df["Address"].values:
        return True
    else:
        return False


def extracted_list() -> list:
    file_path = 'output.xlsx'
    df = pd.read_excel(file_path)
    return df['Entity'].tolist()


def extract_entities(driver: webdriver.Chrome):
    driver.get("https://www.scopescan.ai/vcWatch/Alameda%20Research?network=eth")
    driver.find_element(By.XPATH, "//span[contains(text(),'VC Watch')]").click()
    time.sleep(5)
    for i in range(15):
        try:
            for tr in range(2, 14):
                try:
                    entity = driver.find_element(By.XPATH, f"//tbody/tr[{tr}]/td[2]").text
                    new_data = {'entity': [entity]}
                    new_df = pd.DataFrame(new_data)
                    existing_df = pd.read_csv('entity.csv')
                    updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    updated_df.to_csv('entity.csv', index=False)
                    print(f'New entity = {entity}')
                except Exception as ex:
                    # print(ex)
                    continue
            driver.find_element(By.XPATH, f"//li[@title='{i + 2}']//a[@rel='nofollow']").click()
            time.sleep(2)
        except Exception as eee:
            # print(eee)
            continue
    print('Entity extraction successful')


def extract_data(driver: webdriver.Chrome):
    # df = pd.read_csv('entity.csv')
    # entities = df['entity'].tolist()
    # entities = list(set(entities))
    future_time = datetime.datetime.now() + datetime.timedelta(seconds=120)
    extracted_entities = extracted_list()
    entities = ['Spark Digital Capital', 'Jump trading', 'Galaxy Digital', 'New Form Capital', 'Geeq', 'Robert Leshner',
                'Apollo Capital', 'Kirin Fund', 'Free Compony', 'Infinity Ventures Crypto', 'Future Money Group',
                'hashkey capital', 'Fasanara Capital', 'Bigcoin capital', 'GFS Ventures', 'LD Capital', 'IOSG Ventures',
                'Voyager', 'Oapital', 'drangonfly capital', 'InsurAce Protocol', 'Pantera Capital', 'Celsius Network',
                'Tornado.Cash', 'DeFi Education Fund', 'Kosmos Capital', 'Hegic Development Fund', 'Mechanism Capital',
                'Magnus Capital', '1kx', 'Genesis Trading', 'Longling Capital', 'Digital Finance Group', 'Pluto',
                'Nascent', 'BlockTower Capital', 'ParaFi Capital', 'Delphi Digital', 'Imtoken Venture', 'fund',
                'Maven11', 'Eden Block', 'Fenbushi Capital', 'Hindsight Capital', 'Terra Nova Capital', 'LedgerPrime',
                'BlockWater', 'Sneaky Ventures', 'OCP Capital', 'FalconX', 'TPS Capital', 'Sigil Fund',
                "7 O'Clock Capital", 'Arkstream Capital', 'Amber', 'SevenX Ventures', 'a16z', 'Hello Capital',
                '1inch.exchange', 'Kain Synthetix', 'Caballeros Capital', 'Varys Capital', 'SushiSwap', 'BR Capital',
                'mgnr', 'Paradigm', 'Nexus Mutual Community Fund', 'Momentum 6', 'Zerion', 'Symbolic Capital Partners',
                'BlockFi', 'Framework Ventures', 'Quantstamp', 'Polychain Capital', 'Axis8 Ventures', 'BitScale',
                'Alameda Research', 'Exnetwork Capital', 'DWF Labs', 'FBG Capital', 'yuobi-capital', 'Dragonfly',
                'Origin', 'Maxstealth', 'blck', 'Arca', 'MetaCartel Ventures', 'Celsius', 'Three Arrows Capital', 'KR1',
                'Fantom Foundation Wallet', 'Blockchain Capital', 'Starry Night Capital', 'Wintermure', 'Cumberland',
                'CMS', 'Geoffrey Hayes', 'IDEO CoLab Ventures', 'Chain Capital', 'Coin98 Ventures',
                'Wintermute trading', 'OlympusDAO', 'orthogonal trading', 'CMS Holdings', 'Tiantian Kullander', 'GCR',
                'Polygon Foundation(Investment)', 'OkX Blockdream Ventures', 'DeFi Rate',
                'Master Ventures', 'Max Wolff', 'Struck Capital', 'Dragonfly Capital', 'DeFiance Capital', '0xb1',
                'mStable', 'ConsenSys']
    for entity in entities:
        if entity in extracted_entities:
            print(f'{entity} already available.. ')
            continue
        driver.get(f"https://www.scopescan.ai/vcWatch/{entity}?network=eth")
        time.sleep(5)
        total_data = (driver.find_element(By.XPATH, "//span[@class='ant-select-selection-item']//div[@class='type']")
                      .text.replace('(', '').replace(')', ''))
        print(f'==================== {entity} ====================')
        page = 1
        for i in range(int(int(total_data) / 10) + 1):
            for counter in range(11):
                try:
                    address = driver.find_element(By.XPATH,
                                                  f"//tbody/tr[{counter + 2}]/td[1]/div[1]/div[1]/div[1]/div[1]")
                    driver.execute_script("arguments[0].click();", address)
                    time.sleep(5)
                    driver.switch_to.window(driver.window_handles[1])
                    address_text = driver.find_element(By.XPATH,
                                                       "//div[@class='addressBox noAddressBox']//div[@class='add-txt']").text
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(3)
                    tag = driver.find_element(By.XPATH,
                                              f'//body[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div['
                                              f'1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div['
                                              f'1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div['
                                              f'2]/div[1]/div[1]/div[1]/div[1]/div[2]/table[1]/tbody[1]/tr[{counter + 2}]/td['
                                              f'2]/div/div').text

                    connection = driver.find_element(By.XPATH,
                                                     f'//body[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div['
                                                     f'1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div['
                                                     f'1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div['
                                                     f'3]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div['
                                                     f'2]/table[1]/tbody[1]/tr[{counter + 2}]/td[3]/span[1]').text

                    if datetime.datetime.now() > future_time:
                        print('Put the script in 2 minutes sleep to prevent frequent hits.')
                        time.sleep(120)
                        future_time = datetime.datetime.now() + datetime.timedelta(seconds=120)

                    if is_duplicate(address_text) is False:
                        insert_data_into_excel([[entity, address_text, tag, connection]])
                except:
                    continue

            try:
                driver.find_element(By.XPATH, f"//div[@class='sc-jefHZX jshcbj']//li[@title='{page + 1}']//a["
                                              f"@rel='nofollow']").click()
                time.sleep(3)
                page += 1
            except:
                continue

        print(f'==================== {entity} ====================')


if __name__ == '__main__':
    print('Script start running ...')
    # create_entity()
    # chrome_driver = config_driver()
    # extract_entities(chrome_driver)
    create_output_file()
    chrome_driver = config_driver()
    login(chrome_driver)
    extract_data(chrome_driver)
    print('Script successfully executed!')
