import logging
import sqlite3
from sqlite3 import Error as sqliteError

import requests

# configuration
SQLITE_DB_PATH = ''  # left empty for current directory
EMAIL_TRACER_BASE_URL = 'https://e189-2a09-bac5-49f-101e-00-19b-131.ngrok-free.app'
EMAIL_TRACER_FETCH_OPEN_API_URL = EMAIL_TRACER_BASE_URL + '/email-tracker/api/open-counter'
EMAIL_TRACER_API_KEY = 'django-insecure-n#bd(hj#v1dx+alxyk3)_tg)h6qm+xi26=brznx@p984&!%g$w'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s --> %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def create_db_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
    except sqliteError as ex:
        logging.error(ex)
        exit()
    return conn


def update_opened_counter(conn, receiver_email, opened_counter, last_opened):
    sql = f"UPDATE emails SET email_opened='{True}', opened_counter='{opened_counter}', last_opened_at='{last_opened}' WHERE receiver_email='{receiver_email}'"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def get_email_opened_data(conn):
    res = requests.get(url=EMAIL_TRACER_FETCH_OPEN_API_URL, headers={'secret': EMAIL_TRACER_API_KEY})
    if res.status_code == 200:
        for item in res.json():
            update_opened_counter(conn, item['email'], item['count'], item['last_opened'])
    else:
        logging.error(f'Invalid response from email api service, status = {res.status_code}')


def tracer():
    logging.info('Email Tracer Script starts running ...')
    # send_message_to_slack('SendEmails Script has started running ...')

    # initialize db connection
    conn = create_db_connection(SQLITE_DB_PATH + 'sqlite.db')

    # get data
    get_email_opened_data(conn)

    logging.info('Email Tracer Script executed successfully!')


if __name__ == '__main__':
    tracer()
