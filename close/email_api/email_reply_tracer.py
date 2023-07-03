import email
import imaplib
import logging
import sqlite3
from sqlite3 import Error as sqliteError

from dateutil import parser

# configuration
SQLITE_DB_PATH = 'client_sqlite.db'
EMAIL_SUBJECT = 'Quick question'


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


def update_replied_by_lead(conn, lead_replied, lead_replied_at, email_id):
    sql = f"UPDATE emails SET lead_replied='{lead_replied}', lead_replied_at='{lead_replied_at}' WHERE id='{email_id}'"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def check_email_replies(replied_lead_email, send_date, inbox_cred):
    try:
        # Connect to the SMTP server
        server = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        server.login(inbox_cred[2], inbox_cred[3])

        # Select the inbox folder
        server.select('INBOX')

        # Search for emails with the subject line of the original email you sent
        result, data = server.search(None, f'SUBJECT "{EMAIL_SUBJECT}"')

        if result == "OK":
            for item in [x.decode('utf-8') for x in data][0].split(' '):
                result, data = server.fetch(item, '(RFC822)')
                raw_reply_email = data[0][1]
                reply_email_message = email.message_from_bytes(raw_reply_email)
                reply_email_from = reply_email_message['From'].split('<')[1].split('>')[0]
                reply_email_send_date = parser.parse(reply_email_message['Date'].split(',')[1].strip()).date().strftime(
                    "%m/%d/%Y")

                if parser.parse(reply_email_send_date).date() >= parser.parse(
                        send_date).date() and replied_lead_email.strip() == reply_email_from.strip():
                    server.close()
                    server.logout()
                    return reply_email_message['Date'].split(',')[1].strip()

        # Close the connection to the SMTP server
        server.close()
        server.logout()
        return None

    except Exception as e:
        print(e)
        return None


def get_desired_emails(conn) -> list:
    cursor = conn.execute('SELECT * FROM emails WHERE lead_replied=0 OR lead_replied is NULL')
    return cursor.fetchall()


def get_sender_email_credentials(conn, receiver_email) -> bool:
    cursor = conn.execute("SELECT * FROM connected_accounts WHERE account_email=?", (receiver_email,))
    return cursor.fetchone()


def tracer():
    logging.info('Email reply tracer script starts running ...')

    # initialize db connection
    conn = create_db_connection(SQLITE_DB_PATH)

    # trace lead reply
    data = get_desired_emails(conn)
    for item in data:
        sender_email = item[1]  # item[1] is sender email
        reply_to_email = item[6]  # item[6] is reply to email
        send_date = item[4]
        receiver_email = item[2]

        if reply_to_email in ['', None, ' ']:
            inbox_to_explore = sender_email
        else:
            inbox_to_explore = reply_to_email

        inbox_cred = get_sender_email_credentials(conn, inbox_to_explore)
        result = check_email_replies(receiver_email, send_date, inbox_cred)
        if result is not None:
            update_replied_by_lead(conn, True, parser.parse(result).strftime("%m/%d/%Y %H:%M:%S"), item[0])

    logging.info('Email reply tracer script executed successfully!')


if __name__ == '__main__':
    tracer()
