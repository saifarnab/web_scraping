from datetime import datetime
import logging
import os
import time

import resend
from dotenv import load_dotenv
import db_connectivity

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# read environ
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')
WAITING_TIME = int(os.getenv('WAITING_TIME'))
MAX_EMAIL_SEND_LIMIT_PER_DAY = int(os.getenv('MAX_EMAIL_SEND_LIMIT_PER_DAY'))
TIME_ZONE = os.getenv('TIME_ZONE')


def create_tables(conn):
    _email_table = """ CREATE TABLE IF NOT EXISTS emails (
                                                id INT AUTO_INCREMENT PRIMARY KEY,
                                                contact_email text NOT NULL,
                                                connected_account_email text NOT NULL,
                                                email_template text,
                                                resend_id VARCHAR(100),
                                                reply_to VARCHAR(100),
                                                created_date VARCHAR(100)
                                            ); """

    _contacts_pointer_pointer_table = """ CREATE TABLE IF NOT EXISTS contacts_pointer (
                                                            pointer int DEFAULT 0
                                                        ); """

    try:
        c = conn.cursor()
        c.execute(_email_table)
        c.execute(_contacts_pointer_pointer_table)
    except Exception as ex:
        logging.exception('error while creating table', ex)


def get_contacts(cur) -> list:
    cur.execute("SELECT name, first_name, last_name, title, primary_email FROM contacts")
    return cur.fetchall()


def get_connected_accounts(cur) -> list:
    cur.execute("SELECT account_name, email, reply_to FROM connected_accounts")
    return cur.fetchall()


def pointer_init(conn, cur):
    cur.execute("SELECT * FROM contacts_pointer")
    pointer = cur.fetchone()
    if pointer is None:
        cur.execute("INSERT INTO contacts_pointer (pointer) VALUES (0)")
        conn.commit()


def get_last_pointer(cur) -> int:
    cur.execute("SELECT * FROM contacts_pointer")
    pointer = cur.fetchone()
    return int(pointer[0])


def update_pointer(conn, cur, last_pointer: int):
    cur.execute(f"DELETE FROM contacts_pointer")
    conn.commit()
    sql = f"""INSERT INTO contacts_pointer (pointer) VALUES ('{last_pointer}')"""
    cur.execute(sql)
    conn.commit()


def get_email_template(contacts_first_name: str) -> str:
    return f"""<p dir=\"ltr\" id=\"isPasted\">Hi {contacts_first_name},</p><div color=\"rgb(75, 81, 93)\"><br>I'm curious if you've 
                considered outsourcing your customer support?&nbsp;<br><br>I know that can be a scary thought–but we do things 
                differently than you might have heard about or experienced.</div><div color=\"rgb(75, 81, 93)\"><br></div><div 
                color=\"rgb(75, 81, 93)\">My name is Jim, and I'm the Co-Founder of xFusion. We offer a fully-managed customer 
                support solution with a unique approach that combines human expertise and AI technology.</div>We're convinced 
                that the foundation of outstanding customer support lies in having a valued and inspired team. We prioritize 
                investing in our agents by providing attractive compensation and creating an enjoyable, supportive work 
                atmosphere, which in turn generates top-notch service for our clients and their customers.<br><br>Because we 
                empower our agents with the latest AI tools like ChatGPT and Intercom Fin, they\\'re up to 3x more productive 
                than traditional customer support reps. This combination of technology and talent sets us 
                apart.&nbsp;<br><br>Lastly, we understand the importance of trust when it comes to outsourcing, and we believe 
                it\\'s our responsibility to earn your business. Therefore, no upfront payment is required. If you’re not happy 
                after 30 days, you can walk and not pay a dime.<br><br>If you think having a short conversation makes sense, 
                please let me know.<br><br>Thank you for taking the time to read this, {contacts_first_name}!<br><div color=\"rgb(75, 81, 
                93)\">&nbsp;</div><div color=\"rgb(75, 81, 93)\">Jim - Co-Founder of <a fr-original-style=\"user-select: auto;\" 
                href=\"http://xfusion.io/\" rel=\"noopener noreferrer noopener\" style=\"user-select: 
                auto;\">xFusion.io</a></div><div color=\"rgb(75, 81, 93)\" data-en-clipboard=\"true\" data-pm-slice=\"1 1 []\">(
                If you want me gone like a bad haircut, let me know and I\'ll disappear faster than a toupee in a 
                hurricane)</div>"""


def get_resend_email_params(contact_first_name: str, contact_email: str, connected_account_name: str,
                            connected_account_email: str) -> dict:
    return {
        "from": f"{connected_account_name} <{connected_account_email}>",
        "to": [f"{contact_email}"],
        "subject": EMAIL_SUBJECT,
        "html": get_email_template(contact_first_name),
    }


def send_email_via_resend(contact_first_name: str, contact_email: str, connected_account_name: str,
                          connected_account_email: str) -> (str, str):
    try:
        resend.api_key = RESEND_API_KEY
        params = get_resend_email_params(contact_first_name, contact_email, connected_account_name,
                                         connected_account_email)
        email = resend.Emails.send(params)
        return email.get('id'), params.get('html')
    except Exception as e:
        logging.exception(e)
        return "", ""


def insert_email(conn, cur, data: tuple):
    sql = "INSERT INTO emails (contact_email, connected_account_email, email_template, resend_id, reply_to, created_date) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(sql, data)
    conn.commit()


def get_total_email_send_via_connect_account(cur, connected_account_email: str) -> int:
    cur.execute(
        f"SELECT count(*) FROM emails WHERE connected_account_email='{connected_account_email}' AND created_date='{datetime.now().date().__str__()}'")

    return cur.fetchone()[0]


def email_sender(conn, cur, connected_accounts: list, contacts: list):
    pointer = get_last_pointer(cur)
    while True:
        if pointer >= len(contacts):
            break

        for connected_account in connected_accounts:
            if pointer >= len(contacts):
                break

            if get_total_email_send_via_connect_account(cur, connected_account[1]) > MAX_EMAIL_SEND_LIMIT_PER_DAY:
                logging.info(f'This email {connected_account[1]} reach the max limit of sending email in a day')
                continue
            contact = contacts[pointer]
            resend_id, email_template = send_email_via_resend(contact[1], contact[4], connected_account[0],
                                                              connected_account[1])
            insert_email(conn, cur, (
                contact[4],
                connected_account[1],
                email_template,
                resend_id,
                connected_account[2],
                datetime.now().date()
            ))
            pointer += 1
            logging.info(f'Email send to {contact[4]}')

        update_pointer(conn, cur, pointer)
        logging.info(f'Waiting for {WAITING_TIME} seconds to start sending emails')
        time.sleep(WAITING_TIME)
    logging.info("Successfully send email to all the contacts")


def run():
    conn, cur = db_connectivity.db_connection()
    create_tables(conn)
    pointer_init(conn, cur)
    contacts = get_contacts(cur)
    connected_accounts = get_connected_accounts(cur)
    email_sender(conn, cur, connected_accounts, contacts)


if __name__ == '__main__':
    run()
