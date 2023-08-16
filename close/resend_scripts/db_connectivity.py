import logging
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# read environ
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')


def db_connection():
    try:
        conn = mysql.connector.connect(host=DATABASE_HOST, port=int(DATABASE_PORT), user=DATABASE_USER,
                                       password=DATABASE_PASSWORD, database=DATABASE_NAME)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        logging.exception(e)
        return None, None
