import csv

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree


def get_request_headers() -> dict:
    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36'}


def csv_file_init(file_name: str):
    try:
        with open(file_name, 'x', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(["CompanyName", "Address", "City", "State", "ZipCode", "Telephone", "Link"])
            print('File created successfully.')
    except FileExistsError:
        pass


def write_csv(file_name: str, new_row: list) -> bool:
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)

    return True


def run():
    print('Script Start running ...')
    filename = 'rale.csv'
    csv_file_init(filename)
    cat_links = []
    page = requests.post('https://web.raleighchamber.org/allcategories', headers=get_request_headers())
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        categories = soup.findAll('li', class_="ListingCategories_AllCategories_CATEGORY")
        for category in categories:
            link = 'https://web.raleighchamber.org' + category.find('a', href=True)['href']
            cat_links.append(link)

    page = requests.post('https://web.raleighchamber.org/Advertising-Media', headers=get_request_headers())
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        categories = soup.findAll('li', class_="ListingCategories_AllCategories_CATEGORY")
        for category in categories:
            link = 'https://web.raleighchamber.org' + category.find('a', href=True)['href']
            cat_links.append(link)

    print('Total categories: ', len(cat_links))
    cat_links = cat_links[785 + 231:]
    issues = []

    # cat_links = ['https://web.raleighchamber.org/Banners/Print-My-Images-28241']
    for ind, link in enumerate(cat_links):
        page = requests.post(link, headers=get_request_headers())
        if page.url == 'https://web.raleighchamber.org/allcategories':
            continue
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            dom = etree.HTML(str(soup))
            try:
                if dom.xpath('//a[@class="ListingDetails_Level5_SITELINK"]'):
                    try:
                        name = dom.xpath('//a[@class="ListingDetails_Level5_SITELINK"]')[0].text
                    except Exception:
                        name = ''
                    try:
                        address = dom.xpath('//span[@itemprop="street-address"]')[0].text
                    except Exception:
                        address = ''

                    try:
                        address_2 = dom.xpath('//div[@itemprop="address"]/text()')
                        if address_2 and address_2[0] not in ['', ' ', None, '\n', ',', ', ']:
                            address += f' {address_2[0]}'
                    except Exception:
                        address_2 = ''

                    try:
                        locality = dom.xpath('//span[@itemprop="locality"]')[0].text
                    except Exception:
                        locality = ''

                    try:
                        region = dom.xpath('//span[@itemprop="region"]')[0].text
                    except Exception:
                        region = ''
                    try:
                        postal_code = dom.xpath('//span[@itemprop="postal-code"]')[0].text
                    except Exception:
                        postal_code = ''

                    try:
                        phone = dom.xpath("//span[@class='ListingDetails_Level5_MAINCONTACT']/text()")
                        for item in phone:
                            if str(item).strip() not in ['', ' ', ',', ', ', None]:
                                phone = str(item).strip()
                                break
                    except Exception:
                        phone = ''
                    length = len(dom.xpath('//a[@class="ListingDetails_Level5_SITELINK"]')) - 1
                    print(f"1 -> {link} -> {length}")
                    print(name, address, locality, region, postal_code, phone)

                elif dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a'):
                    try:
                        name = dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a')[0].text
                    except Exception:
                        name = ''
                    try:
                        address = dom.xpath('//span[@itemprop="street-address"]')[0].text
                    except Exception:
                        address = ''

                    try:
                        address_2 = dom.xpath('//div[@itemprop="address"]/text()')
                        if address_2 and address_2[0] not in ['', ' ', None, '\n', ',', ', ']:
                            address += f' {address_2[0]}'
                    except Exception:
                        pass

                    try:
                        locality = dom.xpath('//span[@itemprop="locality"]')[0].text
                    except Exception:
                        locality = ''
                    try:
                        region = dom.xpath('//span[@itemprop="region"]')[0].text
                    except Exception:
                        region = ''
                    try:
                        postal_code = dom.xpath('//span[@itemprop="postal-code"]')[0].text
                    except Exception:
                        postal_code = ''

                    try:
                        phones = dom.xpath("//span[@class='ListingDetails_Level1_MAINCONTACT']/text()")
                        phone = ''
                        for item in phones:
                            if str(item).strip() not in ['', ' ', ',', ', ', None]:
                                phone = str(item).strip()
                                break
                    except Exception:
                        phone = ''

                    length = len(dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a')) - 1
                    print(f"2 -> {link} -> {length}")
                    print(name, address, locality, region, postal_code, phone)
                    write_csv(filename,
                              [name.strip(), address.strip(), locality.strip(), region.strip(), postal_code.strip(),
                               phone.strip(), link])

                elif dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a'):
                    try:
                        name = dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a')[0].text
                    except Exception:
                        name = ''
                    try:
                        address = dom.xpath('//span[@itemprop="street-address"]')[0].text
                    except Exception:
                        address = ''

                    try:
                        address_2 = dom.xpath('//div[@itemprop="address"]/text()')
                        if address_2 and address_2[0] not in ['', ' ', None, '\n', ',', ', ']:
                            address += f' {address_2[0]}'
                    except Exception:
                        pass

                    try:
                        locality = dom.xpath('//span[@itemprop="locality"]')[0].text
                    except Exception:
                        locality = ''
                    try:
                        region = dom.xpath('//span[@itemprop="region"]')[0].text
                    except Exception:
                        region = ''
                    try:
                        postal_code = dom.xpath('//span[@itemprop="postal-code"]')[0].text
                    except Exception:
                        postal_code = ''

                    try:
                        phones = dom.xpath("//span[@class='ListingDetails_Level1_MAINCONTACT']/text()")
                        phone = ''
                        for item in phones:
                            if str(item).strip() not in ['', ' ', ',', ', ', None]:
                                phone = str(item).strip()
                                break
                    except Exception:
                        phone = ''

                    length = len(dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a')) - 1
                    print(f"2 -> {link} -> {length}")
                    print(name, address, locality, region, postal_code, phone)
                    write_csv(filename,
                              [name.strip(), address.strip(), locality.strip(), region.strip(), postal_code.strip(),
                               phone.strip(), link])

                elif dom.xpath('//div[@class="ListingDetails_Level5_HEADERBOXBOX"]//h2//span//span'):
                    try:
                        name = dom.xpath('//div[@class="ListingDetails_Level5_HEADERBOXBOX"]//h2//span//span')[0].text
                    except Exception:
                        name = ''
                    try:
                        address = dom.xpath('//span[@itemprop="street-address"]')[0].text
                    except Exception:
                        address = ''

                    try:
                        address_2 = dom.xpath('//div[@itemprop="address"]/text()')
                        if address_2 and address_2[0] not in ['', ' ', None, '\n', ',', ', ']:
                            address += f' {address_2[0]}'
                    except Exception:
                        pass

                    try:
                        locality = dom.xpath('//span[@itemprop="locality"]')[0].text
                    except Exception:
                        locality = ''
                    try:
                        region = dom.xpath('//span[@itemprop="region"]')[0].text
                    except Exception:
                        region = ''
                    try:
                        postal_code = dom.xpath('//span[@itemprop="postal-code"]')[0].text
                    except Exception:
                        postal_code = ''

                    try:
                        phones = dom.xpath("//span[@class='ListingDetails_Level1_MAINCONTACT']/text()")
                        phone = ''
                        for item in phones:
                            if str(item).strip() not in ['', ' ', ',', ', ', None]:
                                phone = str(item).strip()
                                break
                    except Exception:
                        phone = ''

                    length = len(dom.xpath('//div[@class="ListingDetails_Level1_HEADERBOXBOX"]//h2//a')) - 1
                    print(f"2 -> {link} -> {length}")
                    print(name, address, locality, region, postal_code, phone)
                    write_csv(filename,
                              [name.strip(), address.strip(), locality.strip(), region.strip(), postal_code.strip(),
                               phone.strip(), link])

                elif dom.xpath('//div[@class="ListingResults_All_CONTAINER ListingResults_Level1_CONTAINER"]'):
                    items = dom.xpath('//div[@class="ListingResults_All_CONTAINER ListingResults_Level1_CONTAINER"]')
                    length = len(
                        dom.xpath('//div[@class="ListingResults_All_CONTAINER ListingResults_Level1_CONTAINER"]')) - 1
                    print(f"3 -> {link} -> {length}")
                    for item in items:

                        try:
                            name = item.xpath('.//span[@itemprop="name"]//a')[0].text
                            if name is None:
                                name = ''
                        except Exception:
                            name = ''

                        try:
                            address = item.xpath('.//span[@itemprop="street-address"]')[0].text
                            if address is None:
                                address = ''
                        except Exception:
                            address = ''

                        try:
                            locality = item.xpath('.//span[@itemprop="locality"]')[0].text
                            if locality is None:
                                locality = ''
                        except Exception:
                            locality = ''

                        try:
                            region = item.xpath('.//span[@itemprop="region"]')[0].text
                            if region is None:
                                region = ''
                        except Exception:
                            region = ''

                        try:
                            postal_code = item.xpath('.//span[@itemprop="postal-code"]')[0].text
                            if postal_code is None:
                                postal_code = ''
                        except Exception:
                            postal_code = ''

                        try:
                            phones = item.xpath('.//div[@class="ListingResults_Level1_PHONE1"]/text()')
                            if phones:
                                phone = phones[0]
                            else:
                                phone = ''
                        except Exception:
                            phone = ''

                        try:
                            addresses_2 = item.xpath('.//div[@itemprop="address"]/text()')
                            address_2 = ''
                            for ele in addresses_2:
                                if ele is not None and len(ele) >= 3:
                                    address_2 = ele
                        except Exception:
                            address_2 = ''

                        print(name.strip(), address.strip() + ' ' + address_2.strip(), locality.strip(), region.strip(),
                              postal_code.strip(), phone.strip())
                        write_csv(filename,
                                  [name.strip(), address.strip(), locality.strip(), region.strip(), postal_code.strip(),
                                   phone.strip(), link])

                elif dom.xpath('//div[@id="tabber1"]//p//strong'):
                    no_ele = dom.xpath('//div[@id="tabber1"]//p//strong')
                    if no_ele[
                        0].text == "Based on your search criteria, we did not find any results. Please try to broaden your search.":
                        print(f'4 -> {link}')
                        print('Not company found')
                        continue
                    else:
                        print(f'5 -> {link}')
                        print('New cat')

                elif dom.xpath('//li[@class="ListingCategories_AllCategories_CATEGORY"]'):
                    print(f'6 -> {link}')
                    print('Multiple categories found.')
                    if link not in [
                        'https://web.raleighchamber.org/Advertising-Media',
                        'https://web.raleighchamber.org/Baked-Goods',
                        'https://web.raleighchamber.org/Bankruptcy',
                        'https://web.raleighchamber.org/allcategories',
                        'https://web.raleighchamber.org/Business-Plan-Writing'
                    ]:
                        break
                    continue

                else:
                    print(link)
                    print('other variety found')
                    issues.append(link)
                print(f'Current pointer --> {ind}')

            except Exception as e:
                print(link)
                issues.append(link)

    print('Script successfully completed!')
    df = pd.DataFrame(issues, columns=["link"])
    df.to_csv('issues.csv', index=False)


if __name__ == "__main__":
    run()
