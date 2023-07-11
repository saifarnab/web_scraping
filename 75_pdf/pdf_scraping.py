import copy
import time

import pandas as pd
import pdfplumber
import urllib3
import io

def pdf_scraping():
    data = []
    http = urllib3.PoolManager()
    temp = io.BytesIO()
    temp.write(http.request("GET", "https://www.city-asset.co.uk/s/CAM-Sustainable-Real2-June-2023.pdf").data)
    with pdfplumber.open(temp) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text().split('\n')
            for i in text:
                print(i)

            print('------------------------')




# if __name__ == '__main__':
#     data = pdf_scraping()
#     columns = ['Page', 'Date', 'Reference', 'HMO Landlords', 'Licensee Name', 'Licensee Address', 'Address',
#                'Managers Details', 'Licensee Date', 'Expiry Date', 'Max. Letting units', 'Max Occupants',
#                'Households', 'Persons', 'Terraced', 'Self Contained', 'Non- Self Contained', 'Floors From',
#                'Living Accommodation', 'Sleeping Accommodation', 'Bathrooms/Shower rooms', 'Toilets with Wash Basins',
#                'Kitchens', 'Sinks']
#     df = pd.DataFrame(data, columns=columns)
#     sorted_df = df.sort_values(by=['Licensee Name', 'Licensee Address'], ascending=True)
#     sorted_df.to_excel(f"coventry_hmo/data_re_gen.xlsx", index=False)

if __name__ == '__main__':
    pdf_scraping()