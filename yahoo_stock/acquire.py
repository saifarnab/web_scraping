import subprocess
import datetime
import gspread
import pandas as pd
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

# define google api credentials & scopes
credential = "pf-cloud-apis-995e6222b9da.json"
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def web_driver_config():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36')
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
    chrome_driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    chrome_driver.maximize_window()
    return chrome_driver


def google_service_auth():
    cred = ServiceAccountCredentials.from_json_keyfile_name(credential, scopes=scopes)
    return gspread.authorize(cred)


def scrapper() -> list:
    dataframe = []
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
            date_obj = datetime.datetime.strptime(formatted_date, '%b %d, %Y')
            formatted_date = date_obj.strftime('%d/%m/%Y')
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
            two_hundred_total = 0
            two_hundred_total_last = 0
            for b in range(51):
                if b < 50:
                    fd_total = fd_total + float(FD_element[b].text)
                if b > 0:
                    lfd_total = lfd_total + float(FD_element[b].text)
                if b < 20:
                    td_total = td_total + float(FD_element[b].text)
                if b > 0 and b < 21:
                    ltd_total = ltd_total + float(FD_element[b].text)
                if b < 200:
                    two_hundred_total = two_hundred_total + float(FD_element[b].text)
                if b > 1 and b < 202:
                    two_hundred_total_last = two_hundred_total_last + float(FD_element[b].text)

            fd_average = float("{:.4f}".format(fd_total / 50))
            lfd_average = float("{:.4f}".format(lfd_total / 50))
            td_average = float("{:.4f}".format(td_total / 20))
            ltd_average = float("{:.4f}".format(ltd_total / 20))
            two_hundred_total_avg = float("{:.4f}".format(two_hundred_total / 200))
            two_hundred_total_last_avg = float("{:.4f}".format( two_hundred_total_last / 200))

            dataframe.append(
                [formatted_date, symbol, company_name, closing_price_float, fd_average, td_average, lfd_average,
                 ltd_average, two_hundred_total_avg, two_hundred_total_last_avg])

        except Exception as ex:
            pass
    return dataframe


def create_csv(data: list):
    df = pd.DataFrame(data, columns=['Date', 'Symbol', 'CompanyName', 'ClosingPrice', 'FiftyDayAverage',
                                     'TwentyDayAverage', 'FiftyDayAverageLast', 'TwentyDayAverageLast',
                                     'TwoHundredDayAverage', 'TwoHundredTotalLastAverage'])
    df.to_csv('stock_data.csv', index=False)


if __name__ == "__main__":
    print("Starting_extraction.....")

    # create google api client
    client = google_service_auth()

    # parse worksheet
    stock_basket = client.open('Stocks').worksheet('Stock Basket')

    # get chrome driver
    driver = web_driver_config()

    print('------> acquire code being processed...')

    # extract data.bson
    dataframe = scrapper()

    # create csv
    create_csv(dataframe)

    print(f"{len(dataframe)} data have been extracted.")
    print("Extraction Successfully Completed!!!!")
