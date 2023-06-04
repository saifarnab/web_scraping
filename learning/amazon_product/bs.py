import requests
import time
import pandas as pd
from bs4 import BeautifulSoup


def get_products():
    print('Enter the product name you want to search: ')
    searchable_product = str(input('> '))
    print('Start storing data.bson...')

    # get the number available for the searchable products
    url = f"https://www.amazon.in/s?k={searchable_product}"
    page = requests.post(url)
    time.sleep(2)
    if page.status_code != 200:
        print(f'Get {page.status_code} from the url')
        exit()

    soup = BeautifulSoup(page.content, "lxml")
    pages = soup.find('span', class_="s-pagination-item s-pagination-disabled")
    if pages is None:
        print('Failed to get the number of pages for the searchable product')
        exit()

    total_page = int(pages.text)
    page_number = 1
    data_count = 0
    products_n_price_list = []
    while True:
        url = f"https://www.amazon.in/s?k={searchable_product}&page={page_number}&ref=sr_pg_{page_number}"
        html_page = requests.post(url)
        if page_number >= total_page:
            break
        if html_page.status_code != 200:
            print(f"Get {html_page.status_code} from the url")
            page_number += 1
            continue
        soup = BeautifulSoup(html_page.content, "lxml")
        products = soup.findAll('div', class_='a-section a-spacing-small a-spacing-top-small')
        for ind, product in enumerate(products):
            product_name = product.find('span', class_='a-size-medium a-color-base a-text-normal')
            product_price = product.find('span', class_='a-price-whole')
            if product_name is None or product_price is None:
                continue

            products_n_price_list.append([product_name.text, product_price.text])

        print(f"{data_count} data.bson stored.")
        page_number += 1
        if page_number >= total_page:
            break

    df = pd.DataFrame(products_n_price_list, columns=["Product Name", "Product Price"])
    df.to_excel(f"data.bson/{searchable_product}.xlsx", index=False)


if __name__ == '__main__':
    get_products()
