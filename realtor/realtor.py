import csv
import subprocess

import requests
from bs4 import BeautifulSoup
from lxml import etree

# define api key for scrapper
API_KEY = 'c333d3ec36f9c6e6d5c7969de4bb1695'

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})

# install dependencies
subprocess.check_call(['pip', 'install', 'bs4'])
subprocess.check_call(['pip', 'install', 'requests'])
subprocess.check_call(['pip', 'install', 'lxml'])


def input_params():
    try:
        zip_code = str(input('Enter zip code: '))
        if zip_code == '':
            raise Exception
    except Exception as e:
        print('invalid input for zip code. input must be integer & greater then 0')
        exit()

    try:
        bedrooms = int(input('Enter the number of bedrooms: '))
        if bedrooms < 0:
            raise Exception
    except Exception as e:
        print('invalid input for bedrooms. input must be integer & greater then or equal 0')
        exit()

    try:
        bathrooms = int(input('Enter the number of bathrooms: '))
        if bathrooms < 0:
            raise Exception
    except Exception as e:
        print('invalid input for bathrooms. input must be integer & greater then 0')
        exit()

    min_price = 0
    try:
        min_price = int(input('Enter minimum price: '))
        if min_price < 0:
            raise Exception
    except Exception as e:
        print('invalid input for bathrooms. input must be integer & greater then or equal 0')
        exit()

    try:
        max_price = int(input('Enter maximum price: '))
        if max_price < min_price:
            raise Exception
    except Exception as e:
        print('invalid input for bathrooms. input must be integer, greater then or equal min price')
        exit()

    try:
        category = int(input('Press 1 for `Buy`, Press 2 for `Rent`: '))
        if category not in [1, 2]:
            raise Exception
    except Exception as e:
        print('invalid input for bathrooms. input must be either 1 or 2')
        exit()

    try:
        limit = int(input('How many property you want extract: '))
        if limit < 1:
            raise Exception
    except Exception as e:
        print('invalid input for limit. input must be integer & greater then or equal 1')
        exit()

    return zip_code, bedrooms, bathrooms, min_price, max_price, category, limit


def csv_file_init(file_name: str):
    try:
        with open(file_name, 'x') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(
                ["Category", "Property Type", "Address", "Bedrooms", "Bathrooms", "Price", "Link", "Telephone",
                 "Managed", "Pool", "Furnished"])
            print('File created successfully.')
    except FileExistsError:
        pass


def write_csv(file_name: str, new_row: list) -> bool:
    flag = True
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
    zip_code, bedrooms, bathrooms, min_price, max_price, category, limit = input_params()
    # zip_code, bedrooms, bathrooms, min_price, max_price, category, limit = 33312, 2, 2, 0, 150000, 1, 5
    print('Script starts ...')
    # based on category decide which pages need to scrap
    if category == 1:  # Buy
        file_name = 'buy_data.csv'
        csv_file_init(file_name)
        page = 1
        property_counter = 0
        while True:
            # generate url
            url = f'https://www.realtor.com/realestateandhomes-search/{zip_code}/beds-{bedrooms}/baths-{bathrooms}/price-{min_price}-{max_price}/sby-6/pg-{page}'
            webpage = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            # take all available cards
            property_cards = dom.xpath('//div[@data-testid="property-card"]')
            if len(property_cards) < 1:
                close_program('No data avaialble, exiting program..')

            # iterate each card to extract data
            for property_card in property_cards:
                details_url = \
                    property_card.xpath(
                        '..//div[@data-testid="property-card"]//a[@data-testid="property-anchor"]/@href')[
                        0]
                if details_url is not None:
                    details_url = str(details_url).strip()

                # dig down property page
                details_url = 'https://www.realtor.com' + details_url
                details_page = requests.get(details_url, headers=HEADERS)
                details_soup = BeautifulSoup(details_page.content, "html.parser")
                details_dom = etree.HTML(str(details_soup))

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
                    telephone_parser = details_dom.xpath('//a[@data-testid="office-phone-link"]')
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
                    price = property_card.xpath('..//span[@data-label="pc-price"]')[0].text.strip()
                except Exception as e:
                    price = ''
                try:
                    bed = property_card.xpath('..//li[@data-label="pc-meta-beds"]//span[1]')[0].text.strip()
                except Exception as e:
                    bed = ''
                try:
                    bath = property_card.xpath('..//li[@data-label="pc-meta-baths"]//span[1]')[0].text.strip()
                except Exception as e:
                    bath = ''

                # write to the csv if not exist
                if write_csv(file_name,
                             ['Buy', property_type, address, bed, bath, price, details_url, telephone, '', pool,
                              furnished]) is True:
                    property_counter += 1
                    print(f'--> {property_counter}. New Property added.')

                # exit the program if limit reached
                if property_counter >= limit:
                    close_program('Reached the property extraction limit, existing the program')

            page += 1

    else:  # Rent
        page = 1
        property_counter = 0
        file_name = 'rent_data.csv'
        csv_file_init(file_name)
        # generate url
        url = f'https://www.realtor.com/apartments/{zip_code}/beds-{bedrooms}/baths-{bathrooms}/price-{min_price}-{max_price}/sby-6/pg-{page}'
        webpage = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))

        # take all available cards
        property_cards = dom.xpath('//div[@data-testid="card-content"]')
        if len(property_cards) < 1:
            close_program('All the available property have been extracted based on input params, exiting program..')

        # iterate each card to extract data
        for property_card in property_cards:
            details_url = property_card.xpath('..//a[@data-testid="card-link"]/@href')[0]
            if details_url is not None:
                details_url = str(details_url).strip()

            # dig down property page
            details_url = 'https://www.realtor.com' + details_url
            details_page = requests.get(details_url, headers=HEADERS)
            details_soup = BeautifulSoup(details_page.content, "html.parser")
            details_dom = etree.HTML(str(details_soup))

            # address
            try:
                address = " ".join(details_url.split('/')[-1].split('_')[:-1]).replace('-', " ").replace('_', ' ')
            except Exception as e:
                address = ''

            # property type
            try:
                property_type = details_dom.xpath(
                    '//div[@class="Text__StyledText-rui__sc-19ei9fn-0 wdTNy TypeBody__StyledBody-rui__sc-163o7f1-0 hHKKwr"]')[
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

            telephone = ''
            try:
                if 'tel:' in str(details_soup):
                    telephone = details_soup.find('a', href=lambda href: href and href.startswith('tel:')).text
                else:
                    print(f'Failed to get telephone, retrying...')
                    for i in range(5):
                        page_url = f'https://api.scraperapi.com/?api_key={API_KEY}&url={details_url}'
                        response = requests.get(page_url)
                        ds = BeautifulSoup(response.content, 'html.parser')
                        if 'tel:' in str(ds):
                            telephone = ds.find('a', href=lambda href: href and href.startswith('tel:')).text
                            break
            except Exception as e:
                telephone = ''

            # price, bed & bath
            try:
                price = property_card.xpath('..//div[@data-testid="card-price"]')[0].text
                if price is not None:
                    price = str(price).strip()
            except Exception as e:
                price = ''

            try:
                bed = property_card.xpath('..//li[@data-testid="property-meta-beds"]//span')[0].text
                if bed is not None:
                    bed = str(bed).strip()
            except Exception as e:
                bed = ''

            try:
                bath = property_card.xpath('..//li[@data-testid="property-meta-baths"]//span')[0].text
                if bath is not None:
                    bath = str(bath).strip()
            except Exception as e:
                bath = ''

            # write to the csv if not exist
            if write_csv(file_name, ['Rent', property_type, address, bed, bath, price, details_url, telephone, '', pool,
                                     furnished]) is True:
                property_counter += 1
                print(f'--> {property_counter}. New Property added.')

            # exit the program if limit reached
            if property_counter >= limit:
                close_program('Reached the property extraction limit, existing the program')

        page += 1


if __name__ == "__main__":
    scrapper()
