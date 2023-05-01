import logging
import sqlite3
import time
from sqlite3 import Error as sqliteError
from datetime import date

from closeio_api import Client

CLOSE_API_KEY = 'api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE'  # your close api secret key
USER_ID = 'user_l0UqCXVwEd82vSOui1HxhVAyTAf0hOa9BDxsXizfJhV'
EMAIL_TEMPLATE_ID = 'tmpl_6i4qWyPodtm0pfpJPR19W58EL9LfzNSJfKaPsH98en2'
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
    _connected_accounts_table = """ CREATE TABLE IF NOT EXISTS connected_accounts (
                                                    id integer PRIMARY KEY,
                                                    account_id text UNIQUE NOT NULL,
                                                    account_name text NOT NULL,
                                                    account_email text NOT NULL
                                                ); """
    try:
        c = conn.cursor()
        c.execute(_email_table)
        c.execute(_connected_accounts_table)
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


def create_connected_accounts(conn, accounts):
    for account in accounts:
        try:
            sql = f"""INSERT INTO connected_accounts (account_id, account_name, account_email) VALUES ('{account[0]}','{account[1]}','{account[2]}')"""
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as ex:
            pass


def make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id):
    return {
        "contact_id": contact_id,
        "user_id": USER_ID,
        "lead_id": lead_id,
        "direction": "outgoing",
        "created_by_name": sender_name,
        "sender": f"{sender_name} <{sender_email}>",
        "to": [receiver_email],
        "bcc": [],
        "cc": [],
        "status": "inbox",
        "attachments": [],
        "template_id": EMAIL_TEMPLATE_ID,
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
    r = api.post('/activity/email/', payload)
    print(r)


def get_contacts(api):
    res_data = api.get(f'/contact/')
    return res_data['data']


def check_lead_exist(conn, lead_id) -> bool:
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM leads WHERE lead_id='{lead_id}'")
    count = cur.fetchall()
    if count[0][0] > 0:
        return True
    return False


def run():
    conn = create_db_connection(SQLITE_DB_PATH + 'sqlite.db')
    create_tables(conn)
    api = Client(CLOSE_API_KEY)

    contacts = get_contacts(api)
    sc = get_sender_accounts(api)
    create_connected_accounts(conn, sc)

    counter, success_counter = 0, 0
    while True:
        for ind, sender in enumerate(sc):
            contact = contacts[counter]
            # sender_name = sender[1]
            # sender_email = sender[2]
            sender_name = 'David Tran'
            sender_email = 'david@xfusion.io'
            # if MAX_LIMIT_PER_DAY - get_sender_current_sent_email_count(conn, sender_email) <= 0:
            #     logging.info(f'<{sender_email}> this sender email has exceed the max limit to sent email per day')
            #     continue
            # receiver_email = contact['emails'][0]['email']
            # contact_id = contact['id']
            # lead_id = contact['lead_id']

            receiver_email = 'martin.onami@xfusion.io'
            contact_id = 'emailacct_ZFiotKd2E2n3178diEp7SRY4VMY4Ote5wEbHPIrF532'
            lead_id = 'lead_n44QaRtZXI8fs7l7qhEHTNDxHhqwSxQNkvmh6VZyTmH'

            # if check_lead_exist(conn, lead_id) is False:
            #     logging.info(f'<{lead_id}> this lead id is not available on DB')
            #     counter += 1
            #     continue
            payload = make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id)
            print(payload)
            send_email(api, payload)
            create_email_sent_confirmation(conn, sender_email, receiver_email, date.today().strftime("%m/%d/%Y"))
            counter += 1
            success_counter += 1
            logging.info(f'--> email sent to <{receiver_email}> from <{sender_email}> & confirmation store in DB')
            logging.info(f'--> total successful email sent count = {success_counter}')
            break

        if counter >= len(contacts):
            exit()
        logging.info(f'--> waiting for {WAITING_TIME}s for next email sent..')
        time.sleep(WAITING_TIME)


run()
