import csv

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree

HEADERS = ({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})


def read_excel() -> list:
    # df = pd.read_excel('urls.xlsx')
    # return df['URL'][:10]
    return ['https://www.superpharmacy.com.au/products/airomir-autohaler-100mcg-200-doses']


def csv_file_init(file_name: str):
    with open(file_name, 'x', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            ["Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
             "Option1 Name",
             "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value", "Variant SKU",
             "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
             "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
             "Variant Requires Shipping",
             "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", "Image Alt Text", "Gift Card",
             "SEO Title", "SEO Description", "Google Shopping / Google Product Category",
             "Google Shopping / Gender",
             "Google Shopping / Age Group", "Google Shopping / MPN", "Google Shopping / AdWords Grouping",
             "Google Shopping / AdWords Labels", "Google Shopping / Condition", "Google Shopping / Custom Product"
                                                                                "Google Shopping / Custom Label 0",
             "Google Shopping / Custom Label 1", "Google Shopping / Custom Label 2"
                                                 "Google Shopping / Custom Label 3",
             "Google Shopping / Custom Label 4", "Variant Image", "Variant Weight Unit",
             "Variant Tax Code", "Cost per item", "Price / International", "Compare At Price / International",
             "Status"])

        print('File created successfully.')


def csv_file_init_exp(file_name: str):
    with open(file_name, 'x', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["url"])
        print('Exp File created successfully.')


def write_csv(file_name: str, new_row: list):
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(new_row)


def scrapper():
    file_name = 'shopify_data.csv'
    exp_file_name = 'exp_data.csv'
    csv_file_init(file_name)
    csv_file_init_exp(exp_file_name)
    urls = read_excel()
    for url_ind, url in enumerate(urls):
        try:
            webpage = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            handle = url.split('/')[-1]
            title = dom.cssselect("div[class='title'] h1")[0].text
            description = soup.findAll('dd')[0]
            vendor = 'My Store'
            product_category = ''
            product_type = 'Medicines'

            tags = title
            temp_idx = title.find(')')
            if temp_idx > 0:
                tags = title[:temp_idx + 1]

            published = 'FALSE'
            option1_name = 'Title'
            option1_value = title
            temp_idx = title.find('(')
            if temp_idx > 0:
                option1_value = title[:temp_idx]

            option2_name = ''
            option2_value = ''
            option3_name = ''
            option3_value = ''

            variant_sku = ''

            variant_grams = ''
            # temp1_idx = title.find('(')
            # temp2_idx = title.find(')')
            # if temp1_idx > 0 and temp2_idx > 0:
            #     variant_grams = title[temp1_idx + 1: temp2_idx][:3]

            variant_inv_tracker = 'shopify'
            variant_inv_qty = ''
            variant_inv_policy = 'deny'
            variant_fulfill_service = 'manual'

            price = dom.xpath("//div[@class='pdp__price']")[0].text[1:]
            variant_com_price = ''
            variant_required_shipping = 'TRUE'
            variant_taxable = 'TRUE'
            variant_barcode = ''
            img_srcs_list = []

            img_srcs = dom.xpath('//img[@class="slick-nav-product__image"]')
            if len(img_srcs) == 0:
                img_src = dom.xpath('//img[@class="slick-carousel-product__image"]')
                if len(img_src) > 0:
                    img_src = img_src[0].get('src')
                else:
                    img_src = dom.xpath("//div[@class='slick-carousel-slide']//span//img")[0].get('src')

                img_srcs_list.append(img_src)

            else:
                for img_src in img_srcs:
                    img_srcs_list.append(img_src.get('src'))

            img_alt_txt = ''

            gift_card = 'FALSE'
            seo_title = title
            seo_description = description
            google_shopping_category = 'Home > Pharmacist Medicines'
            google_shopping_gender = 'Unisex'
            google_shopping_age = 'Adult'
            google_shopping_mpn = ''
            google_shopping_adwords_group = 'Medicine'
            google_shopping_adwords_label = ''
            google_shopping_condition = 'new'
            google_shopping_custom_product = 'FALSE'
            google_shopping_custom_label_0 = ''
            google_shopping_custom_label_1 = ''
            google_shopping_custom_label_2 = ''
            google_shopping_custom_label_3 = ''
            google_shopping_custom_label_4 = ''
            variant_img = ''

            variant_weight = ''
            if 'ml' in title:
                variant_weight = 'ml'
            elif 'mcg' in title:
                variant_weight = 'mcg'
            elif 'mg' in title:
                variant_weight = 'mg'
            elif 'g' in title:
                variant_weight = 'g'

            variant_tax_code = ''
            cost_per_item = ''
            price_international = ''
            comp_price_international = ''
            status = 'active'

            for ind, src in enumerate(img_srcs_list):
                if ind == 0:
                    data = [handle, title, description, vendor, product_category, product_type, tags, published, option1_name,
                            option1_value, option2_name, option2_value, option3_name, option3_value, variant_sku, variant_grams,
                            variant_inv_tracker, variant_inv_qty, variant_inv_policy, variant_fulfill_service, price,
                            variant_com_price,
                            variant_required_shipping, variant_taxable, variant_barcode, src, ind+1, img_alt_txt,
                            gift_card,
                            seo_title, seo_description, google_shopping_category, google_shopping_gender, google_shopping_age,
                            google_shopping_mpn, google_shopping_adwords_group, google_shopping_adwords_label,
                            google_shopping_condition,
                            google_shopping_custom_product, google_shopping_custom_label_0, google_shopping_custom_label_1,
                            google_shopping_custom_label_2, google_shopping_custom_label_3, google_shopping_custom_label_4,
                            variant_img, variant_weight, variant_tax_code, cost_per_item, price_international,
                            comp_price_international, status]

                else:
                    data = [handle, '', '', '', '', '', '', '', '',
                            '', '', '', '', '', '', '',
                            '', '', '', '', '',
                            '',
                            '', '', '', src, ind+1, '',
                            '',
                            '', '', '', '', '',
                            '', '', '',
                            '',
                            '', '', '',
                            '', '', '',
                            '', '', '', '', '',
                            '', '']

                write_csv(file_name, data)
            print(f'{url_ind + 1}. inserted -> {title}')
        except Exception as e:
            print(e)
            break
            write_csv(exp_file_name, [url])

    print('Execution done!')


if __name__ == '__main__':
    scrapper()
