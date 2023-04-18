import csv
import logging
import os
import time
import json
import pandas as pd
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from closeio_api import Client

api = Client('api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE')

logging.basicConfig(
    # filename=log_file,
    # filemode='a',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

# Create GoogleDrive instance with authenticated GoogleAuth instance
input_folder_id = '1njV8kYm6ODHyEBK3q_Y3bea2sU14CGwV'
downloads_folder = 'downloads'
g_auth = GoogleAuth()
drive = GoogleDrive(g_auth)

if not os.path.exists(downloads_folder):
    os.mkdir(downloads_folder)

# get all files in the target folder
google_drive_csv_files = drive.ListFile(
    {'q': f"'{input_folder_id}' in parents and trashed=false"}).GetList()

for csv_file in google_drive_csv_files:
    try:
        csv_file_title = csv_file['title']
        local_path = os.path.join(downloads_folder, csv_file_title)
        logging.info(
            f'Downloading {csv_file_title} to local path [{local_path}]...')
        csv_file.GetContentFile(local_path)

        # Read file as panda dataframe
        dataframe = pd.read_csv(f"{downloads_folder}/{csv_file_title}")
        for first_name, company_name, website, individual_li_url, email, phone, company_des, \
                company_li_url in zip(dataframe['FIRST_NAME'], dataframe['COMPANY_NAME'], dataframe['WEBSITE'],
                                      dataframe['INDIVIDUAL_LI_URL'], dataframe['EMAIL'], dataframe['PHONE'],
                                      dataframe['COMPANY_DESCRIPTION'], dataframe['COMPANY_LI_URL']):

            close_api_seamless_request_data = {
                "name": "Bluth Company",
                "url": "http://thebluthcompany.tumblr.com/",
                "description": "Best. Show. Ever.",
                "status_id": "stat_1ZdiZqcSIkoGVnNOyxiEY58eTGQmFNG3LPlEVQ4V7Nk",
                "contacts": [
                    {
                        "name": "Gob",
                        "title": "Sr. Vice President",
                        "emails": [
                            {
                                "type": "office",
                                "email": "gob@example.com"
                            }
                        ],
                        "phones": [
                            {
                                "type": "office",
                                "phone": "8004445555"
                            }
                        ]
                    }
                ],
                "custom.cf_ORxgoOQ5YH1p7lDQzFJ88b4z0j7PLLTRaG66m8bmcKv": "Website contact form",
                "custom.cf_nenE344jkwrjyRRezwsf8b4V1MCoXWIDHIStmFavZks": ["Choice 1", "Choice 2"],
                "custom.cf_FSYEbxYJFsnY9tN1OTAPIF33j7Sw5Lb7Eawll7JzoNh": "Segway",
                "custom.cf_bA7SU4vqaefQLuK5UjZMVpbfHK4SVujTJ9unKCIlTvI": "Real Estate",
                "addresses": [
                    {
                        "label": "business",
                        "address_1": "747 Howard St",
                        "address_2": "Room 3",
                        "city": "San Francisco",
                        "state": "CA",
                        "zipcode": "94103",
                        "country": "US",
                    }
                ]
            }

            #
            # # post a lead
            # lead = api.post('lead', data=close_api_seamless_request_data)
            # print(lead)
            leads = api.get('lead/lead_0w4cZytr85zTf2jYwaYDxaFZie1PGDP9cflZD45JEQO')
            print(leads)



    except Exception as e:
        print(e)
