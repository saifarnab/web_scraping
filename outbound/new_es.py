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
                                                sender_email text NOT NULL,
                                                receiver_email text NOT NULL,
                                                sending_date text NOT NULL
                                            ); """
    _connected_accounts_table = """ CREATE TABLE IF NOT EXISTS connected_accounts (
                                                    id integer PRIMARY KEY,
                                                    account_name text NOT NULL,
                                                    account_email text NOT NULL,
                                                    account_password text,
                                                    send_via_close boolean NOT NULL
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


def create_email_sent_confirmation(conn, sender_email, receiver_email, sending_date):
    sql = f"""INSERT INTO emails (sender_email, receiver_email, sending_date) VALUES ('{sender_email}','{receiver_email}', '{sending_date}')"""
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


def get_connected_accounts(conn):
    cursor = conn.execute("SELECT * FROM connected_accounts")
    return cursor.fetchall()


def check_email_already_send(conn, receiver_email) -> bool:
    cursor = conn.execute("SELECT * FROM emails WHERE receiver_email=?", (receiver_email,))
    if len(cursor.fetchall()) == 0:
        return False
    return True


def assign_timestamp_with_limit(connected_accounts: list) -> dict:
    data = {}
    for connected_account in connected_accounts:
        data[connected_account[2]] = {'timestamp': time.time(), 'limit': 0}
    return data


def update_timestamp_with_limit(connected_accounts_time_limits, sender_email):
    print(connected_accounts_time_limits[sender_email])
    timestamp, limit = connected_accounts_time_limits[sender_email]['timestamp'], connected_accounts_time_limits[sender_email]['limit']
    connected_accounts_time_limits[sender_email] = {'timestamp': time.time() + 960, 'limit': limit + 1}
    print(connected_accounts_time_limits[sender_email])


def check_connected_account_availability(data: dict, connect_account_email: str) -> bool:
    try:
        if time.time() > data[connect_account_email]['timestamp'] and data[connect_account_email]['limit'] <= 30:
            return True
        return False
    except Exception as ex:
        return False


def run():
    # initialize db connection
    conn = create_db_connection(SQLITE_DB_PATH + 'sqlite.db')

    # create tables
    create_tables(conn)

    # create close api instance
    api = Client(CLOSE_API_KEY)

    # fetch all the available contacts from close
    contacts = get_contacts(api)

    # fetch all the available connected accounts from db
    connected_accounts = get_connected_accounts(conn)

    # assign timestamp & per execution sending limit to all the connected accounts
    connected_accounts_time_limits = assign_timestamp_with_limit(connected_accounts)

    # total number of contacts
    total_contacts = len(contacts)

    # looping all the connected accounts to send email
    contacts_pointer = 0
    for connected_account in connected_accounts:

        # check whether the connected account is available to send email
        if check_connected_account_availability(connected_accounts_time_limits, connected_account[2]) is False:
            continue

        # take a single contact to sent email
        while check_email_already_send(conn, contacts[contacts_pointer]['emails'][0]['email']) is True:
            contacts_pointer += 1

        # exit the program if email sends to all the contacts
        if contacts_pointer >= total_contacts:
            break
        contact = contacts[contacts_pointer]

        # extract required data
        receiver_email = contact['emails'][0]['email']
        contact_id = contact['id']
        lead_id = contact['lead_id']
        sender_name = connected_account[1]
        sender_email = connected_account[2]

        # make decision which service to use (close or gmail)
        if connected_account[4]:  # this connected account configured to send email via close

            # generate payload to send email
            payload = make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id)

            # send email to close
            # send_email(api, payload)

            # create confirmation entry in email table
            # create_email_sent_confirmation(conn, sender_email, receiver_email, date.today().strftime("%m/%d/%Y"))

            # update the timestamp & limit for the used connected account
            update_timestamp_with_limit(connected_accounts_time_limits, sender_email)
        else:
            pass

    # sc = get_sender_accounts(api)
    # print(sc[0])
    # print(sc[1])

    # print(contacts[0])

    # contacts = get_contacts(api)
    # sc = get_sender_accounts(api)
    # create_connected_accounts(conn, sc)
    #
    # counter, success_counter = 0, 0
    # while True:
    #     for ind, sender in enumerate(sc):
    #         contact = contacts[counter]
    #         # sender_name = sender[1]
    #         # sender_email = sender[2]
    #         sender_name = 'David Tran'
    #         sender_email = 'david@xfusion.io'
    #         # if MAX_LIMIT_PER_DAY - get_sender_current_sent_email_count(conn, sender_email) <= 0:
    #         #     logging.info(f'<{sender_email}> this sender email has exceed the max limit to sent email per day')
    #         #     continue
    #         # receiver_email = contact['emails'][0]['email']
    #         # contact_id = contact['id']
    #         # lead_id = contact['lead_id']
    #
    #         receiver_email = 'martin.onami@xfusion.io'
    #         contact_id = 'emailacct_ZFiotKd2E2n3178diEp7SRY4VMY4Ote5wEbHPIrF532'
    #         lead_id = 'lead_n44QaRtZXI8fs7l7qhEHTNDxHhqwSxQNkvmh6VZyTmH'
    #
    #         # if check_lead_exist(conn, lead_id) is False:
    #         #     logging.info(f'<{lead_id}> this lead id is not available on DB')
    #         #     counter += 1
    #         #     continue
    #         payload = make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id)
    #         print(payload)
    #         send_email(api, payload)
    #         create_email_sent_confirmation(conn, sender_email, receiver_email, date.today().strftime("%m/%d/%Y"))
    #         counter += 1
    #         success_counter += 1
    #         logging.info(f'--> email sent to <{receiver_email}> from <{sender_email}> & confirmation store in DB')
    #         logging.info(f'--> total successful email sent count = {success_counter}')
    #         break
    #
    #     if counter >= len(contacts):
    #         exit()
    #     logging.info(f'--> waiting for {WAITING_TIME}s for next email sent..')
    #     time.sleep(WAITING_TIME)


run()
