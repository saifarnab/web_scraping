import logging
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

import db_connectivity
import email_template as et

load_dotenv()
logging.basicConfig(level=logging.DEBUG)


class Resend:

    def __init__(self):
        # envs
        self.resend_api_url = os.getenv('RESEND_API_URL')
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        self.email_subject = os.getenv('EMAIL_SUBJECT')
        self.waiting_time = int(os.getenv('WAITING_TIME'))
        self.limit = int(os.getenv('MAX_EMAIL_SEND_LIMIT_PER_DAY'))
        self.time_zone = os.getenv('TIME_ZONE')
        self.primary_reply_to = os.getenv('PRIMARY_REPLY_TO')

        # db connections
        self.conn = None
        self.cursor = None

    def _set(self):
        self.conn, self.cursor = db_connectivity.db_connection()

    def _create_tables(self):
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
            self.cursor.execute(_email_table)
            self.cursor.execute(_contacts_pointer_pointer_table)
        except Exception as ex:
            logging.exception('error while creating table', ex)

    def _get_contacts(self) -> list:
        self.cursor.execute("SELECT name, first_name, last_name, title, primary_email FROM contacts")
        return self.cursor.fetchall()

    def _get_connected_accounts(self) -> list:
        self.cursor.execute("SELECT account_name, email, reply_to FROM connected_accounts")
        return self.cursor.fetchall()

    def _pointer_init(self):
        self.cursor.execute("SELECT * FROM contacts_pointer")
        pointer = self.cursor.fetchone()
        if pointer is None:
            self.cursor.execute("INSERT INTO contacts_pointer (pointer) VALUES (0)")
            self.conn.commit()

    def _get_last_pointer(self) -> int:
        self.cursor.execute("SELECT * FROM contacts_pointer")
        pointer = self.cursor.fetchone()
        return int(pointer[0])

    def _update_pointer(self, last_pointer: int):
        self.cursor.execute(f"DELETE FROM contacts_pointer")
        self.conn.commit()
        sql = f"""INSERT INTO contacts_pointer (pointer) VALUES ('{last_pointer}')"""
        self.cursor.execute(sql)
        self.conn.commit()

    def _get_resend_email_params(self, contact_first_name: str, contact_email: str, connected_account_name: str,
                                 connected_account_email: str) -> dict:
        email_template = et.Template(contact_first_name).get_email_template()
        return {
            "from": f"{connected_account_name} <{connected_account_email}>",
            "to": [f"{contact_email}"],
            "subject": self.email_subject,
            "html": email_template,
            "reply_to": [self.primary_reply_to]
        }

    def _send_email_via_resend(self, contact_first_name: str, contact_email: str, connected_account_name: str,
                               connected_account_email: str) -> (str, str):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.resend_api_key}"
            }
            body = self._get_resend_email_params(contact_first_name, contact_email, connected_account_name,
                                                 connected_account_email)
            requests.post(self.resend_api_url, json=body, headers=headers)
        except Exception as e:
            logging.exception(e)

    def _insert_email(self, data: tuple):
        sql = "INSERT INTO emails (contact_email, connected_account_email, email_template, resend_id, reply_to, created_date) VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(sql, data)
        self.conn.commit()

    def _get_total_email_send_via_connect_account(self, connected_account_email: str) -> int:
        self.cursor.execute(
            f"SELECT count(*) FROM emails WHERE connected_account_email='{connected_account_email}' AND created_date='{datetime.now().date().__str__()}'")

        return self.cursor.fetchone()[0]

    def _email_sender(self, connected_accounts: list, contacts: list):
        pointer = self._get_last_pointer()
        while True:
            if pointer >= len(contacts):
                break

            for connected_account in connected_accounts:
                if pointer >= len(contacts):
                    break

                if self._get_total_email_send_via_connect_account(connected_account[1]) > MAX_EMAIL_SEND_LIMIT_PER_DAY:
                    logging.info(f'This email {connected_account[1]} reach the max limit of sending email in a day')
                    continue
                contact = contacts[pointer]
                resend_id, email_template = self._send_email_via_resend(contact[1], contact[4], connected_account[0],
                                                                        connected_account[1])
                self._insert_email((
                    contact[4],
                    connected_account[1],
                    email_template,
                    resend_id,
                    connected_account[2],
                    datetime.now().date()
                ))
                pointer += 1
                logging.info(f'Email send to {contact[4]}')

            self._update_pointer(pointer)
            logging.info(f'Waiting for {self.waiting_time} seconds to start sending emails')
            time.sleep(self.waiting_time)
        logging.info("Successfully send email to all the contacts")

    def processor(self):
        self._set()
        self._create_tables()
        self._pointer_init()
        contacts = self._get_contacts()
        connected_accounts = self._get_connected_accounts()
        self._email_sender(connected_accounts, contacts)


if __name__ == '__main__':
    Resend().processor()
