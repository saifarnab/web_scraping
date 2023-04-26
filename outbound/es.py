import logging
import sqlite3
import time
from sqlite3 import Error as sqliteError
from datetime import date

from closeio_api import Client

CLOSE_API_KEY = 'api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE'  # your close api secret key
USER_ID = 'user_l0UqCXVwEd82vSOui1HxhVAyTAf0hOa9BDxsXizfJhV'
SQLITE_DB_PATH = ''  # left empty for current directory
MAX_LIMIT_PER_DAY = 30  # maximum amount of email a sender can sent per day
WAITING_TIME = 3600  # wait time for next email sending in seconds

# log format
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)


def create_tables(conn):
    _email_table = """ CREATE TABLE IF NOT EXISTS emails (
                                                id integer PRIMARY KEY,
                                                sender text NOT NULL,
                                                receiver text NOT NULL,
                                                sending_date text NOT NULL
                                            ); """
    try:
        c = conn.cursor()
        c.execute(_email_table)
    except sqliteError as ex:
        logging.error('error while creating table', ex)


def create_db_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqliteError as ex:
        print(ex)
        exit()
    return conn


def create_email_sent_confirmation(conn, sender, receiver, sending_date):
    sql = f"""INSERT INTO emails (sender, receiver, sending_date) VALUES ('{sender}','{receiver}', '{sending_date}')"""
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id):
    return {
        "contact_id": contact_id,
        "user_id": USER_ID,
        "lead_id": lead_id,
        "direction": "outgoing",
        "created_by_name": sender_name,
        "date_created": date.today().isoformat(),
        "sender": sender_email,
        "to": [receiver_email],
        "bcc": [],
        "cc": [],
        "status": "inbox",
        "attachments": [],
        "template_id": 'tmpl_6i4qWyPodtm0pfpJPR19W58EL9LfzNSJfKaPsH98en2'
    }


def get_sender_accounts(api) -> list:
    sender_accounts = []
    res_data = api.get('/connected_account/')
    data = res_data['data']
    for item in data:
        sender_accounts.append([item['id'], item['identities'][0]['name'], item['identities'][0]['email']])
    return sender_accounts


def get_sender_current_sent_email_count(conn, sender) -> int:
    cur = conn.cursor()
    cur.execute(
        f"SELECT COUNT(sender) FROM emails WHERE sender='{sender}' AND sending_date='{date.today().strftime('%m/%d/%Y')}'")
    rows = cur.fetchall()
    return rows[0][0]


def send_email(api, payload):
    api.post('/activity/email/', payload)


def get_contacts(api):
    res_data = api.get(f'/contact/')
    return res_data['data']


def run():
    conn = create_db_connection(SQLITE_DB_PATH + 'sqlite.db')
    create_tables(conn)
    api = Client(CLOSE_API_KEY)

    contacts = get_contacts(api)
    sc = get_sender_accounts(api)

    for contact in contacts:
        for each_sender_account in sc:
            sender_name = each_sender_account[1]
            sender_email = each_sender_account[2]
            if MAX_LIMIT_PER_DAY - get_sender_current_sent_email_count(conn, sender_email) <= 0:
                continue
            receiver_email = contact['emails'][0]['email']
            contact_id = contact['id']
            lead_id = contact['lead_id']
            payload = make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id)
            send_email(api, payload)
            create_email_sent_confirmation(conn, sender_email, receiver_email, date.today().strftime("%m/%d/%Y"))
        time.sleep(WAITING_TIME)


run()
