import subprocess

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from webdriver_manager.chrome import ChromeDriverManager

# install dependencies
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'webdriver_manager'])
subprocess.check_call(['pip', 'install', 'numpy'])
subprocess.check_call(['pip', 'install', 'gspread'])
subprocess.check_call(['pip', 'install', 'oauth2client'])

# chrome webdriver config
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
# options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("lang=en-GB")
chrome_options.add_argument('--ignore-certificate-errors')
# self.options.add_argument('--lang=en')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
# self.options.add_argument("--log-level=OFF")
chrome_options.add_argument("--log-level=3")
# driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()

# define google api scopes
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# google service auth
cred = ServiceAccountCredentials.from_json_keyfile_name("<secret-key.json>", scopes=scopes)
client = gspread.authorize(cred)

# parse worksheet
stock_basket = client.open('Stocks').worksheet('Stock Basket')
market_data = client.open('Stocks').worksheet('MarketData')
next_available_row = len(list(filter(None, market_data.col_values(1)))) + 1

print("Starting_extraction.....")

extracted_data_count = 0
for item in stock_basket.get_all_records():
    try:
        url = "https://finance.yahoo.com/quote/" + item['Symbol'] + "/history" + "?p=" + item['Symbol']
        driver.get(url)
        time.sleep(4)
        try:
            cs = "#myLightboxContainer > section > button.Pos\(a\).T\(20px\).End\(20px\).P\(4px\).Bd\(0\).Bgc\(t\).M\(0\) > svg"
            driver.find_element(By.CSS_SELECTOR, cs).click()
        except:
            pass

        time.sleep(4)
        cs = "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(1) > td.Py\(10px\).Ta\(start\).Pend\(10px\) > span"
        formatted_date = driver.find_element(By.CSS_SELECTOR, cs).text
        symbol = item['Symbol']
        company_name = item['Stock Name']
        cs = "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(1) > td:nth-child(5) > span"
        closing_price = driver.find_element(By.CSS_SELECTOR, cs).text
        closing_price_float = float(closing_price)
        cs = "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(n) > td:nth-child(5) > span"
        FD_element = driver.find_elements(By.CSS_SELECTOR, cs)
        fd_total = 0
        lfd_total = 0
        td_total = 0
        ltd_total = 0
        for b in range(51):
            if b < 50:
                fd_total = fd_total + float(FD_element[b].text)
            if b > 0:
                lfd_total = lfd_total + float(FD_element[b].text)
            if b < 20:
                td_total = td_total + float(FD_element[b].text)
            if b > 0 and b < 21:
                ltd_total = ltd_total + float(FD_element[b].text)

        fd_average = fd_total / 50
        lfd_average = lfd_total / 50
        td_average = td_total / 20
        ltd_average = ltd_total / 20

        dataframe = [formatted_date, symbol, company_name, closing_price, fd_average, td_average, lfd_average,
                     ltd_average]
        market_data.insert_row(dataframe, next_available_row)
        next_available_row += 1
        extracted_data_count += 1
        print('------> New Data Added to `MarketData` worksheet.')

    except Exception as ex:
        pass
        # print(f"Website is not responding, failed to extract data for the stock name `{item['Stock Name']}`")

print(f"{extracted_data_count} data have been extracted.")
print("Extraction Successfully Completed!!!!")
