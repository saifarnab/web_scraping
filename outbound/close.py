import logging
import math
import os
import sqlite3
import subprocess
import time
from sqlite3 import Error

import closeio_api
import pandas as pd
from closeio_api import Client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# install dependencies
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'PyDrive'])
subprocess.check_call(['pip', 'install', 'closeio'])

# required keys & path
# your close api secret key
CLOSE_API_KEY = 'api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE'

INPUT_FOLDER_ID = '1njV8kYm6ODHyEBK3q_Y3bea2sU14CGwV'  # input folder id
OUTPUT_FOLDER_ID = '1_zC_gVWLlzktJe4KYqyLF13oQyr7Pefu'  # output folder id

DOWNLOAD_FOLDER_PATH = 'downloads-close'  # left as it is for current directory
SQLITE_DB_PATH = ''  # left empty for current directory

# required custom field id for close
COMPANY_DESCRIPTION_ID = 'cf_1Ojv34J6JICroikPTpA7p688vXTdQN9sxk67NBVWPfF'
COMPANY_LINKEDIN_ID = 'cf_4PA7FtCCanVzoatHEWSlBA5x3wrcbi3yPj9Sqxiwp0f'
COMPANY_EMPLOYEE_COUNT_ID = 'cf_Bhd9bU7oEJNZflcvhNTtePHG19W7NsPOkDbFX3S7pMP'
CONTACT_LINKEDIN_ID = 'cf_7F0p3Qt8YRTMHYp8XyPeFCMOpPzdIOpW0qdqQ5DWYQD'
CONTACT_POSITION_ID = 'cf_EjGBqY7dy2vMm6bnpYgbn5KHUrpeb4fPqjD6J0Ju0b9'
INDUSTRY_ID = 'cf_oKY2l4uq8xINd9jb6YXZb2N4QTD2ynniRfE6RtCohcX'
SENIORITY_ID = 'cf_oKY2l4uq8xINd9jb6YXZb2N4QTD2ynniRfE6RtCohcX'
NUM_EMPLOYEES_ID = 'cf_oKY2l4uq8xINd9jb6YXZb2N4QTD2ynniRfE6RtCohcX'
PENDING_STATUS_ID = 'stat_iqhy3Y2HGaKltd4nFEh77DWAv7zQOxuHE0zawknQJDA'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def check_email_exists(conn, email):
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE email=?", (email,))
    rows = cur.fetchall()
    return len(rows) > 0


def create_sqlite_db(file):
    conn = None
    try:
        conn = sqlite3.connect(file)
    except Error as ex:
        logging.error('error while creating db', ex.__str__())
    logging.info('sqlite db connect success.')
    return conn


def create_tables(conn):
    _leads_table = """ CREATE TABLE IF NOT EXISTS leads (
                                                id integer PRIMARY KEY,
                                                lead_id text NOT NULL,
                                                date_time text NOT NULL
                                            ); """
    _contacts_table = """ CREATE TABLE IF NOT EXISTS contacts (
                                                    id integer PRIMARY KEY,
                                                    lead_ref_id text NOT NULL,
                                                    first_name text,
                                                    last_name text,
                                                    company_name text,
                                                    url text,
                                                    individual_li_url text,
                                                    company_li_url text,
                                                    email text,
                                                    phone text,
                                                    industry text,
                                                    title text,
                                                    seniority text,
                                                    num_employees text,
                                                    first_email_send boolean,
                                                    date_time text NOT NULL
                                                ); """
    try:
        c = conn.cursor()
        c.execute(_leads_table)
        c.execute(_contacts_table)
    except Error as ex:
        logging.error('error while creating table', ex)


def create_lead(conn, value):
    sql = ''' INSERT INTO leads(lead_id,date_time) VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, value)
    conn.commit()
    return cur.lastrowid


def create_contact(conn, value):
    sql = ''' INSERT INTO contacts(lead_ref_id,first_name,last_name,company_name,url,individual_li_url,company_li_url,
    email,phone,industry,title,seniority,num_employees,first_email_send,date_time) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, value)
    conn.commit()
    return cur.lastrowid


def create_file_download_folder():
    if not os.path.exists(DOWNLOAD_FOLDER_PATH):
        os.mkdir(DOWNLOAD_FOLDER_PATH)


def make_close_client():
    return Client(CLOSE_API_KEY)


def make_close_payload(first_name, last_name, company_name, url, individual_li_url, email, phone, industry, company_des,
                       company_li_url, title, seniority, num_employees: str) -> dict:
    return {
        "name": company_name.strip(),
        "url": url.strip(),
        "description": company_des.strip(),
        "contacts": [
            {
                "name": f"{first_name.strip()} {last_name.strip()}",
                "title": title.strip(),
                "emails": [
                    {
                        "type": "office",
                        "email": email.strip()
                    }
                ],
                "phones": [
                    {
                        "type": "office",
                        "phone": phone.strip()
                    }
                ],
                'status_id': PENDING_STATUS_ID.strip(),
                'custom.{}'.format(
                    CONTACT_LINKEDIN_ID): None if individual_li_url.strip() == '' else individual_li_url.strip(),
            }
        ],
        "addresses": [],
        'custom.{}'.format(COMPANY_DESCRIPTION_ID): None if company_des.strip() == '' else company_des.strip(),
        'custom.{}'.format(COMPANY_LINKEDIN_ID): None if company_li_url.strip() == '' else company_li_url.strip(),
        'custom.{}'.format(INDUSTRY_ID): None if industry.strip() == '' else industry.strip(),
        'custom.{}'.format(SENIORITY_ID): None if seniority.strip() == '' else seniority.strip(),
        'custom.{}'.format(NUM_EMPLOYEES_ID): None if num_employees.strip() == '' else num_employees.strip(),
    }


def modified_df_columns(dataframe):
    if 'COMPANY_NAME_FOR_EMAILS' in dataframe.columns and 'COMPANY_NAME' not in dataframe.columns:
        dataframe = dataframe.rename(
            columns={'COMPANY_NAME_FOR_EMAILS': 'COMPANY_NAME'})
    if 'FIRST_NAME' not in dataframe.columns:
        dataframe['FIRST_NAME'] = ' '
    if 'LAST_NAME' not in dataframe.columns:
        dataframe['LAST_NAME'] = ' '
    if 'COMPANY_DESCRIPTION' not in dataframe.columns:
        dataframe['COMPANY_DESCRIPTION'] = ' '
    if 'COMPANY_NAME' not in dataframe.columns:
        dataframe['COMPANY_NAME'] = ' '
    if 'WEBSITE' not in dataframe.columns:
        dataframe['WEBSITE'] = ' '
    if 'INDIVIDUAL_LI_URL' not in dataframe.columns:
        dataframe['INDIVIDUAL_LI_URL'] = ' '
    if 'EMAIL' not in dataframe.columns:
        dataframe['EMAIL'] = ' '
    if 'PHONE' not in dataframe.columns:
        dataframe['PHONE'] = ' '
    if 'COMPANY_LI_URL' not in dataframe.columns:
        dataframe['COMPANY_LI_URL'] = ' '
    if 'INDUSTRY' not in dataframe.columns:
        dataframe['INDUSTRY'] = ' '
    if 'TITLE' not in dataframe.columns:
        dataframe['TITLE'] = ' '
    if 'SENIORITY' not in dataframe.columns:
        dataframe['SENIORITY'] = ' '
    if 'NUM_EMPLOYEES' not in dataframe.columns:
        dataframe['NUM_EMPLOYEES'] = ' '

    return dataframe.fillna("").astype(str)


# check input & output folder exists or not
def check_gdrive_folder_id_exists(drive, folder_id):
    try:
        drive.ListFile(
            {'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    except Exception as ex:
        logging.error(f"folder id ({folder_id}) is not found")
        exit()


# get all files in the target folder
def get_google_drive_csv_files(drive, folder_id) -> list:
    return drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()


def move_gdrive_file(drive, file_id, folder_id):
    file = drive.CreateFile({'id': file_id})
    file.Upload()
    file['parents'] = [{"kind": "drive#parentReference", "id": folder_id}]
    file.Upload()
    logging.info('files move to output folder')


def add_activity_note(client, lead_id: str, note: str = 'Added from Outbound API Automation'):
    client.post('activity/note', data={"note": note, "lead_id": lead_id})
    logging.info("note pushed to close")


def run():
    g_auth = GoogleAuth()
    g_auth.LocalWebserverAuth()
    drive = GoogleDrive(g_auth)
    check_gdrive_folder_id_exists(drive, INPUT_FOLDER_ID)
    check_gdrive_folder_id_exists(drive, OUTPUT_FOLDER_ID)
    create_file_download_folder()
    conn = create_sqlite_db(SQLITE_DB_PATH + 'sqlite.db')
    create_tables(conn)

    api = closeio_api.Client(CLOSE_API_KEY)

    logging.info('----------------- START RUNNING --------------------')
    for csv_file in get_google_drive_csv_files(drive, INPUT_FOLDER_ID):
        try:
            csv_file_title = csv_file['title']
            csv_file_id = csv_file['id']
            local_path = os.path.join(DOWNLOAD_FOLDER_PATH, csv_file_title)
            logging.info(
                f'Downloading {csv_file_title} to local path <{local_path}>...')
            csv_file.GetContentFile(local_path)

            # Read file as panda dataframe
            dataframe = pd.read_csv(f"{DOWNLOAD_FOLDER_PATH}/{csv_file_title}")

            # modify dataframe fields if required
            dataframe = modified_df_columns(dataframe)
            for first_name, last_name, company_name, url, individual_li_url, email, phone, company_des, \
                company_li_url, industry, \
                title, seniority, num_employees in zip(dataframe['FIRST_NAME'], dataframe['LAST_NAME'],
                                                       dataframe['COMPANY_NAME'], dataframe['WEBSITE'],
                                                       dataframe['INDIVIDUAL_LI_URL'], dataframe['EMAIL'],
                                                       dataframe['PHONE'], dataframe['COMPANY_DESCRIPTION'],
                                                       dataframe['COMPANY_LI_URL'], dataframe['INDUSTRY'],
                                                       dataframe['TITLE'], dataframe['SENIORITY'],
                                                       dataframe['NUM_EMPLOYEES']):

                if not check_email_exists(conn, email):
                    # make close api payload
                    payload = make_close_payload(first_name, last_name, company_name, url, individual_li_url, email, phone,
                                                 industry, company_des, company_li_url, title, seniority, num_employees)

                    # post a lead
                    res_data = api.post('lead', data=payload)

                    if res_data.get('id') not in ['', None]:

                        # send activity note
                        add_activity_note(api, res_data.get('id'))

                        # save to db
                        create_contact(conn, (
                            create_lead(
                                conn, (res_data['id'], res_data['date_created'])), first_name, last_name,
                            company_name, url, individual_li_url, company_li_url, email, phone, industry, title, seniority,
                            num_employees, False, res_data['date_created']))

                        logging.info(
                            f'data send to close api and save to db for <{first_name.strip() + " " + last_name.strip()}>')

                    # handle error with rate limit
                    elif res_data.get('error'):
                        if res_data.get('error').get('rate_reset'):
                            rate_reset = math.ceil(res_data.get(
                                'error').get('rate_reset')) + 1
                            logging.error(
                                f"{res_data.get('error').get('message')}, wait for {rate_reset}s")
                            time.sleep(rate_reset)
                    else:
                        logging.error('unknown error', res_data)
                        logging.info(f'Duplicate email found for {first_name.strip()} {last_name.strip()} with email {email.strip()}, skipping this lead')

            move_gdrive_file(drive, csv_file_id, OUTPUT_FOLDER_ID)

        except Exception as ex:
            logging.error(ex)

    # close db connection
    conn.close()
    logging.info('----------------- EXECUTION DONE --------------------')


run()