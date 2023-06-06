import logging
import sqlite3
from sqlite3 import Error as sqliteError

import requests

# configuration
SQLITE_DB_PATH = ''  # left empty for current directory
EMAIL_TRACER_BASE_URL = 'https://d8b9-2a09-bac5-49f-101e-00-19b-131.ngrok-free.app'
EMAIL_TRACER_FETCH_OPEN_API_URL = EMAIL_TRACER_BASE_URL + '/email-tracker/api/open-counter'
EMAIL_TRACER_API_KEY = 'emailtracerB3ldJfYdp65j2iisO9ruBev2Lq7WrUaezy1bEJ14NFHyHIs9DSNu9'

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
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
    sql = f"UPDATE emails SET opened_counter='{opened_counter}', last_opened='{last_opened}' WHERE receiver_email='{receiver_email}'"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def get_email_opened_data(conn):
    res = requests.get(url=EMAIL_TRACER_FETCH_OPEN_API_URL, headers={'secret': EMAIL_TRACER_API_KEY})
    if res.status_code == 200:
        for item in res.json():
            update_opened_counter(conn, item['email'], item['count'], item['last_opened'])


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
