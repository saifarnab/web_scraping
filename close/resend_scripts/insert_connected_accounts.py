import os
import logging
from dateutil import parser
import mysql.connector
from dotenv import load_dotenv
import pandas as pd

import db_connectivity

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# read environ
CONNECTED_ACCOUNTS_FILE_PATH = os.getenv('CONNECTED_ACCOUNTS_FILE_PATH')


def create_tables(connection, cursor):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS connected_accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_name VARCHAR(255),
            email VARCHAR(255),
            reply_to VARCHAR(255),
            created_date VARCHAR(100)
        )
    """

    cursor.execute(create_table_query)
    connection.commit()


# read data from the csv file path
def read_data():
    df = pd.read_csv(CONNECTED_ACCOUNTS_FILE_PATH, dtype=str)
    df = df.fillna('')

    df = df[['account_name', 'email', 'reply_to', 'created_date']]

    new_data = []
    for index, row in df.iterrows():
        new_data.append([row['account_name'], row['email'], row['reply_to'], row['created_date']])

    return new_data


def check_duplicate_email(cur, email):
    try:
        # Execute a query to fetch existing primary email addresses
        query = "SELECT email FROM connected_accounts"
        cur.execute(query)
        existing_emails = [row[0] for row in cur.fetchall()]
        if email in existing_emails:
            logging.info(f"Email '{email}' already exists in the database")
            return True
        else:
            return False

    except mysql.connector.Error as e:
        logging.exception(e)
        return False


def parse_datetime(datetime_str: str):
    return parser.parse(datetime_str).strftime('%d/%m/%Y %H:%M').__str__()


def insert_db(conn, cur, data):
    for item in data:
        if check_duplicate_email(cur, item[1]) is False:
            sql = "INSERT INTO connected_accounts (account_name, email, reply_to, created_date) VALUES (%s, %s, %s, %s)"
            item[3] = parse_datetime(item[3])
            cur.execute(sql, item)
            conn.commit()
    conn.close()
    logging.info('Data inserted successfully.')


def run():
    data = read_data()
    conn, cur = db_connectivity.db_connection()
    create_tables(conn, cur)
    insert_db(conn, cur, data)


if __name__ == '__main__':
    run()
