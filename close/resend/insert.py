import os
import logging

import mysql.connector
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# read environ
FILE_PATH = os.getenv('FILE_PATH')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')


# setup MySQL connection
def db_connection():
    try:
        conn = mysql.connector.connect(host=DATABASE_HOST, port=int(DATABASE_PORT), user=DATABASE_USER,
                                       password=DATABASE_PASSWORD, database=DATABASE_NAME)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        logging.exception(e)


def create_tables(connection, cursor):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS contacts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            title VARCHAR(255),
            primary_phone VARCHAR(255),
            other_phones VARCHAR(255),
            primary_email VARCHAR(255),
            other_emails VARCHAR(255),
            linkedin_profile VARCHAR(255),
            custom_first_phone VARCHAR(255),
            date_created DATETIME,
            lead_id VARCHAR(255),
            lead_display_name VARCHAR(255),
            lead_url VARCHAR(255),
            lead_status_label VARCHAR(255),
            lead_custom_company_address VARCHAR(255),
            lead_custom_company_city VARCHAR(255),
            lead_custom_company_country VARCHAR(255),
            lead_custom_company_description TEXT,
            lead_custom_company_industry VARCHAR(255),
            lead_custom_company_li_profile VARCHAR(255),
            lead_custom_company_linkedin VARCHAR(255),
            lead_custom_company_phone VARCHAR(255),
            lead_custom_company_phone1 VARCHAR(255),
            lead_custom_company_state VARCHAR(255),
            lead_custom_contact_job_title VARCHAR(255),
            lead_custom_contact_li_profile_url VARCHAR(255),
            lead_custom_contact_linkedin_profile VARCHAR(255),
            lead_custom_contact_location VARCHAR(255),
            lead_custom_contact_phone_number VARCHAR(255),
            lead_custom_contact_state VARCHAR(255),
            lead_custom_corporate_phone VARCHAR(255),
            lead_custom_person_assigned VARCHAR(255),
            lead_custom_person_linkedin_url VARCHAR(255),
            lead_html_url VARCHAR(255)
        )
    """

    cursor.execute(create_table_query)
    connection.commit()


# read data from the csv file path
def read_data():
    df = pd.read_csv(FILE_PATH, dtype=str)
    df = df.fillna('')

    df = df[['name', 'first_name', 'last_name', 'title', 'primary_phone', 'other_phones', 'primary_email',
             'other_emails', 'custom.Contact LinkedIn Profile', 'custom.First Phone', 'date_created', 'lead_id',
             'lead_display_name', 'lead_url', 'lead_status_label', 'lead_custom.Company Address',
             'lead_custom.Company City', 'lead_custom.Company Country', 'lead_custom.Company Description',
             'lead_custom.Company Industry', 'lead_custom.Company LI Profile Url', 'lead_custom.Company LinkedIn',
             'lead_custom.Company Phone', 'lead_custom.Company Phone 1', 'lead_custom.Company State',
             'lead_custom.Contact City', 'lead_custom.Contact Job Title', 'lead_custom.Contact LI Profile URL',
             'lead_custom.Contact LinkedIn Profile', 'lead_custom.Contact Location',
             'lead_custom.Contact Phone Number', 'lead_custom.Contact State', 'lead_custom.Corporate Phone',
             'lead_custom.Person Assigned', 'lead_custom.Person Linkedin Url', 'lead_html_url']]

    new_data = []
    for index, row in df.iterrows():
        new_data.append(
            (row['name'], row['first_name'], row['last_name'], row['title'], row['primary_phone'], row['other_phones'],
             row['primary_email'], row['other_emails'], row['custom.Contact LinkedIn Profile'],
             row['custom.First Phone'],
             row['date_created'], row['lead_id'], row['lead_display_name'], row['lead_url'], row['lead_status_label'],
             row['lead_custom.Company Address'], row['lead_custom.Company City'], row['lead_custom.Company Country'],
             row['lead_custom.Company Description'], row['lead_custom.Company Industry'],
             row['lead_custom.Company LI Profile Url'], row['lead_custom.Company LinkedIn'],
             row['lead_custom.Company Phone'], row['lead_custom.Company Phone 1'], row['lead_custom.Company State'],
             row['lead_custom.Contact City'], row['lead_custom.Contact Job Title'],
             row['lead_custom.Contact LI Profile URL'],
             row['lead_custom.Contact LinkedIn Profile'], row['lead_custom.Contact Location'],
             row['lead_custom.Contact Phone Number'],
             row['lead_custom.Contact State'], row['lead_custom.Corporate Phone'], row['lead_custom.Person Assigned'],
             row['lead_custom.Person Linkedin Url'], row['lead_html_url']))

    return new_data


def check_duplicate_email(cur, email):
    try:
        # Execute a query to fetch existing primary email addresses
        query = "SELECT primary_email FROM contacts"
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


def insert_db(conn, cur, data):
    for item in data:
        if check_duplicate_email(cur, item[6]) is False:
            sql = f"INSERT INTO contacts (name, first_name, last_name, title, primary_phone, other_phones, " \
                  f"primary_email, other_emails, linkedin_profile, custom_first_phone, date_created, lead_id, " \
                  f"lead_display_name, lead_url, lead_status_label, lead_custom_company_address, lead_custom_company_city, " \
                  f"lead_custom_company_country, lead_custom_company_description, lead_custom_company_industry, " \
                  f"lead_custom_company_li_profile, lead_custom_company_linkedin, lead_custom_company_phone, " \
                  f"lead_custom_company_phone1, lead_custom_company_state, lead_custom_contact_job_title, " \
                  f"lead_custom_contact_li_profile_url, lead_custom_contact_linkedin_profile, lead_custom_contact_location, " \
                  f"lead_custom_contact_phone_number, lead_custom_contact_state, lead_custom_corporate_phone, " \
                  f"lead_custom_person_assigned, lead_custom_person_linkedin_url, lead_html_url) " \
                  f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                  f"%s, %s %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, item)
            conn.commit()
    conn.close()
    logging.info('Data inserted successfully.')


def run():
    data = read_data()
    conn, cur = db_connection()
    create_tables(conn, cur)
    insert_db(conn, cur, data)


if __name__ == '__main__':
    run()
