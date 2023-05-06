import time

from bs4 import BeautifulSoup
from lxml import etree
import requests

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})


def input_params():
    try:
        zip_code = int(input('Enter zip code: '))
        if zip_code < 1:
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
        print('invalid input for bathrooms. input must be integer & greater then or equal 0')
        exit()

    return zip_code, bedrooms, bathrooms, min_price, max_price, category


def scrapper():
    # take parameters as input
    # zip_code, bedrooms, bathrooms, min_price, max_price, category = input_params()
    zip_code, bedrooms, bathrooms, min_price, max_price, category = 33312, 2, 2, 0, 150000, 1

    # based on category decide which pages need to scrap
    if category == 1:  # Buy
        page = 1

        while True:
            # generate url
            url = f'https://www.realtor.com/realestateandhomes-search/{zip_code}/beds-{bedrooms}/baths-{bathrooms}/price-{min_price}-{max_price}/sby-6/pg-{page}'
            webpage = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            # take all available cards
            property_cards = dom.xpath('//div[@data-testid="property-card"]')
            if len(property_cards) < 1:
                break

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

                price = property_card.xpath('..//span[@data-label="pc-price"]')[0].text
                if price is not None:
                    price = str(price).strip()
                bed = property_card.xpath('..//li[@data-label="pc-meta-beds"]//span[1]')[0].text
                if bed is not None:
                    bed = str(bed).strip()
                bath = property_card.xpath('..//li[@data-label="pc-meta-baths"]//span[1]')[0].text
                if bed is not None:
                    bath = str(bath).strip()

                print(page, details_url, address, price, bed, bath, pool, furnished, telephone)

            page += 1

    else:  # Rent
        pass


if __name__ == "__main__":
    scrapper()
