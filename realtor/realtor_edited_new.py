import csv
import subprocess
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By


# install dependencies
subprocess.check_call(['pip', 'install', 'bs4'])
subprocess.check_call(['pip', 'install', 'requests'])
subprocess.check_call(['pip', 'install', 'lxml'])
subprocess.check_call(['pip', 'install', 'selenium'])
subprocess.check_call(['pip', 'install', 'fake_useragent'])

# define variables
ZIP_CODE = 'Fort-Lauderdale_FL'  # Area -> Fort Lauderdale = Fort-Lauderdal_FL, Scottsdale = Scottsdale_AZ
TYPE = 'single-family-home'
# buy choices -> multi-family-home, mfd-mobile-home, farms-ranches, land, condo, townhome, single-family-home,any
# rent choices -> condo, townhome, single-family-home, apartments, any
BEDROOMS = '3'
BATHROOMS = '3'
MIN_PRICE = '4700'
MAX_PRICE = '5100'
CATEGORY = 'rent'  # choices -> buy, rent
KEYWORDS = ''
STARTING_PAGE = 1 # pages

# define api key for scrapper
API_KEY = 'c333d3ec36f9c6e6d5c7969de4bb1695'

HEADERS = ({'User-Agent': UserAgent().random})


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    return webdriver.Chrome(options=chrome_options)


def csv_file_init(file_name: str):
    try:
        with open(file_name, 'x', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                ["Category", "Property Type", "Address", "Bedrooms", "Bathrooms", "Price", "Link", "Telephone",
                 "Managed", "Pool", "Furnished"])
            print('File created successfully.')
    except FileExistsError:
        pass


def write_csv(file_name: str, new_row: list) -> bool:
    flag = True
    add_hyperlink = f'=HYPERLINK("{new_row[6]}","{new_row[6]}")'
    new_row[6] = add_hyperlink
    with open(file_name, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            if line and new_row[6].strip() == line[6].strip() and new_row[0].strip() == line[0].strip():
                flag = False
                break

    if flag is False:
        print('This property already available ignoring..')
        return False

    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)

    return True


def close_program(msg: str):
    print(msg)
    print('Script successfully executed!')
    exit()


def scrapper():
    # take parameters as input
    print('---------------------------******----------------------')
    print('Script starts ...')

    # based on category decide which pages need to scrap
    if CATEGORY.lower() == 'buy':
        file_name = 'buy_properties.csv'
        csv_file_init(file_name)
        page = STARTING_PAGE
        property_counter = 0
        while True:
            # generate url
            if TYPE.lower() in ['', 'any']:
                url = f'https://www.realtor.com/realestateandhomes-search/{ZIP_CODE}/beds-{BEDROOMS}/baths-{BATHROOMS}/price-{MIN_PRICE}-{MAX_PRICE}/keyword-{KEYWORDS}/sby-6/pg-{page}'
            else:
                url = f'https://www.realtor.com/realestateandhomes-search/{ZIP_CODE}/beds-{BEDROOMS}/baths-{BATHROOMS}/type-{TYPE.lower()}/price-{MIN_PRICE}-{MAX_PRICE}/keyword-{KEYWORDS}/sby-6/pg-{page}'

            print(f'scrapping from --> {url}')
            print(f'Page number = {page}')

            while True:
                webpage = requests.get(url, headers=HEADERS)
                if webpage.status_code == 200:
                    break

                page_url = f'https://api.scraperapi.com/?api_key={API_KEY}&url={url}'
                webpage = requests.get(page_url)
                if webpage.status_code != 200:
                    print('Realtor blocks your IP, will re-try after 60 seconds... ')
                    time.sleep(60)
                else:
                    break

            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            # take all available cards
            property_cards = dom.xpath('//div[@data.bson-testid="property-card"]')
            if len(property_cards) < 1:
                close_program('No data.bson avaialble, exiting program..')

            # iterate each card to extract data.bson
            for property_card in property_cards:
                details_url = \
                    property_card.xpath(
                        '..//div[@data.bson-testid="property-card"]//a[@data.bson-testid="property-anchor"]/@href')[0]
                if details_url is not None:
                    details_url = str(details_url).strip()

                # dig down property page
                while True:
                    details_url = 'https://www.realtor.com' + details_url
                    d_webpage = requests.get(details_url, headers=HEADERS)
                    if d_webpage.status_code == 200:
                        break

                    d_page_url = f'https://api.scraperapi.com/?api_key={API_KEY}&url={details_url}'
                    d_webpage = requests.get(d_page_url)
                    if d_webpage.status_code != 200:
                        print('Realtor blocks your IP, will re-try after 60 seconds... ')
                        time.sleep(60)
                    else:
                        break

                details_soup = BeautifulSoup(d_webpage.content, "html.parser")
                details_dom = etree.HTML(str(details_soup))

                # managed
                managed = ''
                try:
                    providers = details_dom.xpath('//div[@class="provider-data.bson"]//ul[@class="content"]')
                    for provider in providers:
                        items = provider.xpath('..//li')
                        if 'Brokered by' in items[0].text:
                            if items[1].text not in [None, '']:
                                managed = items[1].text
                            elif items[1].xpath('..//span'):
                                managed = items[1].xpath('..//span')[0].text

                            elif len(details_dom.xpath('//a[@data.bson-testid="provider-link"]')) == 2:
                                managed = details_dom.xpath('//a[@data.bson-testid="provider-link"]')[1].text

                            elif len(details_dom.xpath('//a[@data.bson-testid="provider-link"]')) == 1:
                                managed = details_dom.xpath('//a[@data.bson-testid="provider-link"]')[0].text

                    if managed is None:
                        managed = ''

                except Exception as e:
                    print(f'Exception detected - {details_url}')
                    managed = ''

                # property type
                try:
                    property_type = details_dom.xpath(
                        '//div[@class="Text__StyledText-rui__sc-19ei9fn-0 eXfzyb TypeBody__StyledBody-rui__sc-163o7f1-0 gVxVge"]')[
                        0].text
                except Exception as e:
                    property_type = ''

                # pool & furnished feature
                pool, furnished = 'N', 'N'
                if 'Pool and Spa' in str(details_soup):
                    pool = 'Y'
                if 'Furnished Description: Unfurnished' in str(details_soup):
                    furnished = 'N'
                elif 'Furnished Description' in str(details_soup):
                    furnished = 'Y'

                # take the broker telephone number
                try:
                    telephone = ''
                    telephone_parser = details_dom.xpath('//a[@data.bson-testid="office-phone-link"]')
                    if telephone_parser:
                        telephone = telephone_parser[0].text
                except Exception as e:
                    telephone = ''

                # take address
                try:
                    address = details_dom.xpath(
                        '//h1[@class="Text__StyledText-rui__sc-19ei9fn-0 dEYYQ TypeBody__StyledBody-rui__sc-163o7f1-0 gVxVge"]')[
                        0].text.strip()
                except Exception as e:
                    address = ''

                # price, bed & bath
                try:
                    price = property_card.xpath('..//span[@data.bson-label="pc-price"]')[0].text.strip()
                except Exception as e:
                    price = ''
                try:
                    bed = property_card.xpath('..//li[@data.bson-label="pc-meta-beds"]//span[1]')[0].text.strip()
                except Exception as e:
                    bed = ''
                try:
                    bath = property_card.xpath('..//li[@data.bson-label="pc-meta-baths"]//span[1]')[0].text.strip()
                except Exception as e:
                    bath = ''

                # write to the csv if not exist
                if write_csv(file_name,
                             ['Buy', str(property_type), str(address), str(bed).replace('-', 'to'),
                              str(bath).replace('-', 'to'), str(price), str(details_url),
                              str(telephone), str(managed), str(pool), str(furnished)]) is True:
                    property_counter += 1
                    print(f'--> {property_counter}. New Property added.')

            page += 1

    elif CATEGORY.lower() == 'rent':  # Rent
        file_name = 'rent_properties.csv'
        csv_file_init(file_name)
        page = STARTING_PAGE
        property_counter = 0
        while True:
            # generate url
            if TYPE.lower() in ['', 'any']:
                url = f'https://www.realtor.com/apartments/{ZIP_CODE}/beds-{BEDROOMS}/baths-{BATHROOMS}/price-{MIN_PRICE}-{MAX_PRICE}/keyword-{KEYWORDS}/sby-6/pg-{page}'
            else:
                url = f'https://www.realtor.com/apartments/{ZIP_CODE}/beds-{BEDROOMS}/baths-{BATHROOMS}/type-{TYPE.lower()}/price-{MIN_PRICE}-{MAX_PRICE}/keyword-{KEYWORDS}/sby-6/pg-{page}'

            print(f'scrapping from --> {url}')
            print(f'Page number = {page}')

            while True:
                webpage = requests.get(url, headers=HEADERS)
                if webpage.status_code == 200:
                    break

                soup = BeautifulSoup(webpage.content, "html.parser")
                dom = etree.HTML(str(soup))
                if dom.xpath('//div[@class="ErrorPageContentstyles__StyledErrorPageContent-rui__sc-1q6mu8g-0 glxCkW error-404"]'):
                    print('Script successfully executed!')
                    exit()

                page_url = f'https://api.scraperapi.com/?api_key={API_KEY}&url={url}'
                webpage = requests.get(page_url)
                if webpage.status_code != 200:
                    if dom.xpath(
                            '//div[@class="ErrorPageContentstyles__StyledErrorPageContent-rui__sc-1q6mu8g-0 glxCkW error-404"]'):
                        print('Script successfully executed!')
                        exit()
                    print('Realtor blocks your IP, will re-try after 60 seconds... ')
                    time.sleep(60)
                else:
                    break
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            # take all available cards
            property_cards = dom.xpath(
                '//section[@class="PropertiesList_propertiesContainer__7NakV PropertiesList_listViewGrid__TYNow"]//div[@data.bson-testid="card-content"]')
            if len(property_cards) < 1:
                close_program('All the available property have been extracted based on input params, exiting program..')

            # iterate each card to extract data.bson
            for property_card in property_cards:
                details_url = property_card.xpath('..//a[@data.bson-testid="card-link"]/@href')[0]
                if details_url is not None:
                    details_url = str(details_url).strip()

                # dig down property page
                while True:
                    details_url = 'https://www.realtor.com' + details_url
                    d_webpage = requests.get(details_url, headers=HEADERS)
                    if d_webpage.status_code == 200:
                        break

                    d_page_url = f'https://api.scraperapi.com/?api_key={API_KEY}&url={details_url}'
                    d_webpage = requests.get(d_page_url)
                    if d_webpage.status_code != 200:
                        print('Realtor blocks your IP, will re-try after 60 seconds... ')
                        time.sleep(60)
                    else:
                        break
                details_soup = BeautifulSoup(d_webpage.content, "html.parser")
                details_dom = etree.HTML(str(details_soup))

                # address
                try:
                    address = " ".join(details_url.split('/')[-1].split('_')[:-1]).replace('-', " ").replace('_', ' ')
                except Exception as e:
                    address = ''

                if '?' in address:
                    address = address.split('?')[0]

                # property type
                try:
                    property_type = details_dom.xpath(
                        '//li[@class="ListingKeyFactItemstyles__StyledListingKeyFactItem-rui__sc-1txoqt4-0 '
                        'gIIZKk"]//div[@class="Text__StyledText-rui__sc-19ei9fn-0 wdTNy '
                        'TypeBody__StyledBody-rui__sc-163o7f1-0 hHKKwr"]')[
                        0].text
                except Exception as e:
                    property_type = ''

                # pool & furnished feature
                pool, furnished = 'N', 'N'
                if 'Pool' in str(details_soup) or 'Pool and Spa' in str(details_soup):
                    pool = 'Y'
                if 'Unfurnished' in str(details_soup):
                    furnished = 'N'
                elif 'Furnished' in str(details_soup):
                    furnished = 'Y'

                managed_by = ''
                telephone = ''

                counter = 0
                while True:
                    counter += 1
                    if counter >= 3:
                        break
                    try:
                        driver = config_driver()
                        print(driver.title)
                        if 'Pardon' in driver.title:
                            print('Realtor blocks your IP, will re-try after 60 seconds... ')
                            time.sleep(60)
                            counter -= 1
                            continue
                        telephones = driver.find_elements(By.XPATH, '//a[@data.bson-testid="action-button"]')
                        if len(telephones) > 0:
                            telephone = telephones[0].text
                        driver.close()
                        if telephone != '':
                            break

                    except Exception as e:
                        pass

                # price, bed & bath
                try:
                    price = property_card.xpath('..//div[@data.bson-testid="card-price"]')[0].text
                    if price is not None:
                        price = str(price).strip()
                except Exception as e:
                    price = ''

                try:
                    bed = property_card.xpath('..//li[@data.bson-testid="property-meta-beds"]//span')[0].text
                    if bed is not None:
                        bed = str(bed).strip()
                except Exception as e:
                    bed = ''

                try:
                    bath = property_card.xpath('..//li[@data.bson-testid="property-meta-baths"]//span')[0].text
                    if bath is not None:
                        bath = str(bath).strip()
                except Exception as e:
                    bath = ''

                # write to the csv if not exist
                if write_csv(file_name,
                             ['Rent', str(property_type), str(address), str(bed).replace('-', 'to'),
                              str(bath).replace('-', 'to'), str(price),
                              str(details_url),
                              str(telephone), str(managed_by), str(pool), str(furnished)]) is True:
                    property_counter += 1
                    print(f'--> {property_counter}. New Property added.')

            page += 1

    else:
        print('invalid category choices')


if __name__ == "__main__":
    scrapper()
