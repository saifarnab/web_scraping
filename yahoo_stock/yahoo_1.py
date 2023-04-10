print("Environment Creating......")
import subprocess
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'webdriver_manager'])
subprocess.check_call(['pip', 'install', 'numpy'])
subprocess.check_call(['pip', 'install', 'gspread'])
subprocess.check_call(['pip', 'install', 'oauth2client'])
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from webdriver_manager.chrome import ChromeDriverManager

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

scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
cred = ServiceAccountCredentials.from_json_keyfile_name("secret_key.json", scopes=scopes)
file = gspread.authorize(cred)
workbook = file.open("DF_collection")
sheet = workbook.sheet1
inp = pd.read_excel("input.xlsx")
# https://finance.yahoo.com/quote/ILU.AX/history?p=ILU.AX
print("Starting_extraction.....")

gc = pd.DataFrame()

for a in range(len(inp)):
    url = "https://finance.yahoo.com/quote/" + inp.Symbol[a] + "/history" + "?p=" + inp.Symbol[a]
    driver.get(url)
    time.sleep(2)
    try:
        driver.find_element(By.CSS_SELECTOR,
                            "#myLightboxContainer > section > button.Pos\(a\).T\(20px\).End\(20px\).P\(4px\).Bd\(0\).Bgc\(t\).M\(0\) > svg").click()
    except:
        pass
    #     time.sleep(2)
    #     driver.find_element(By.CSS_SELECTOR,"#quote-nav > ul > li:nth-child(5) > a").click()

    time.sleep(4)
    formatted_date = driver.find_element(By.CSS_SELECTOR,
                                         "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(1) > td.Py\(10px\).Ta\(start\).Pend\(10px\) > span").text
    # today = date.today()
    # formatted_date = today.strftime("%d/%m/%Y")
    symbol = inp.Symbol[a]
    company_name = inp.Stock_Name[a]
    closing_price = driver.find_element(By.CSS_SELECTOR,
                                        "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(1) > td:nth-child(5) > span").text
    closing_price_float = float(closing_price)
    FD_element = driver.find_elements(By.CSS_SELECTOR,
                                      "#Col1-1-HistoricalDataTable-Proxy > section > div.Pb\(10px\).Ovx\(a\).W\(100\%\) > table > tbody > tr:nth-child(n) > td:nth-child(5) > span")
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

    Dic = {'Date': formatted_date, 'Symbol': symbol, 'CompanyName': company_name, 'ClosingPrice': float(closing_price),
           'FiftyDayAverage': float(fd_average), 'TwentyDayAverage': float(td_average),
           'FiftyDayAverageLast': float(lfd_average), 'TwentyDayAverageLast': float(ltd_average), 'Check': ""}
    gc = pd.concat([gc, pd.DataFrame([Dic])], ignore_index=True)
    sheet.update(f"A{a + 2}:H{a + 2}", [
        [formatted_date, symbol, company_name, closing_price, fd_average, td_average, lfd_average, ltd_average]])
    gc.loc[:,
    ['Date', 'Symbol', 'CompanyName', 'ClosingPrice', 'FiftyDayAverage', 'TwentyDayAverage', 'FiftyDayAverageLast',
     'TwentyDayAverageLast', 'Check']].to_excel("yahoo.xlsx", index=False)
    print(f"Extracted {len(gc)} Data")
print("Extraction Successfully Completed!!!!")
