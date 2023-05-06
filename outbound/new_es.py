import logging
import math
import sqlite3
import time
from sqlite3 import Error as sqliteError
from datetime import date

from closeio_api import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CLOSE_API_KEY = 'api_6UOHiS0CDzQtMWeUePrqfX.6dMY8E1N4Nzu3i3olfEDPE'  # your close api secret key
USER_ID = 'user_l0UqCXVwEd82vSOui1HxhVAyTAf0hOa9BDxsXizfJhV'
EMAIL_TEMPLATE_ID = 'tmpl_6i4qWyPodtm0pfpJPR19W58EL9LfzNSJfKaPsH98en2'
SQLITE_DB_PATH = ''  # left empty for current directory

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
                                                send_via_close boolean NOT NULL,
                                                sending_date text NOT NULL
                                            ); """
    _connected_accounts_table = """ CREATE TABLE IF NOT EXISTS connected_accounts (
                                                    id integer PRIMARY KEY,
                                                    account_name text NOT NULL,
                                                    account_email text NOT NULL,
                                                    account_password text,
                                                    send_via_close boolean NOT NULL,
                                                    reply_to text
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
        logging.error(ex)
        exit()
    return conn


def create_email_sent_confirmation(conn, sender_email, receiver_email, send_via_close, sending_date):
    sql = f"""INSERT INTO emails (sender_email, receiver_email, send_via_close, sending_date) VALUES ('{sender_email}','{receiver_email}', '{send_via_close}', '{sending_date}')"""
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
        "sender": f"{sender_name} <{sender_email}>",
        "to": [receiver_email],
        "bcc": [],
        "cc": [],
        "status": "outbox",
        "attachments": [],
        "template_id": EMAIL_TEMPLATE_ID,
    }


def send_email_via_close(api, payload):
    res_data = api.post('/activity/email/', payload)
    if res_data.get('id') not in ['', None]:
        return True

    # handle rate limit
    if res_data.get('error'):
        if res_data.get('error').get('rate_reset'):
            rate_reset = math.ceil(res_data.get('error').get('rate_reset')) + 1
            logging.info(f"{res_data.get('error').get('message')}, wait for {rate_reset}s")
            time.sleep(rate_reset)
    return False


def send_email_via_google(sender_email, sender_pass, receiver_email, receiver_name, reply_to: str) -> bool:
    try:

        # set up the SMTP server connection
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = sender_email
        smtp_password = sender_pass  # need to generate app password, your regular gmail pass won't work
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.starttls()
        smtp_connection.login(smtp_username, smtp_password)

        # set up the email message
        body = f"""<p dir=\"ltr\" id=\"isPasted\">Hi {receiver_name.split(' ')[0]},</p><div color=\"rgb(75, 81, 93)\">I'm curious if you've 
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
                    please let me know.<br><br>Thank you for taking the time to read this, {receiver_name.split(' ')[0]}!<br><div color=\"rgb(75, 81, 
                    93)\">&nbsp;</div><div color=\"rgb(75, 81, 93)\">Jim - Co-Founder of <a fr-original-style=\"user-select: auto;\" 
                    href=\"http://xfusion.io/\" rel=\"noopener noreferrer noopener\" style=\"user-select: 
                    auto;\">xFusion.io</a></div><div color=\"rgb(75, 81, 93)\" data-en-clipboard=\"true\" data-pm-slice=\"1 1 []\">(
                    If you want me gone like a bad haircut, let me know and I\\'ll disappear faster than a toupee in a 
                    hurricane)</div>"""
        html = f"""
        <html>
          <head></head>
          <body>
                {body}
          </body>
        </html>
        """

        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = receiver_email
        if reply_to:
            message['reply-to'] = reply_to
        message['Subject'] = 'Quick question'
        html_part = MIMEText(html, 'html')
        message.attach(html_part)

        # send the email
        smtp_connection.sendmail(sender_email, receiver_email, message.as_string())

        # close the SMTP server connection
        smtp_connection.quit()
        return True

    except Exception as ex:
        return False


def get_contacts(api):
    res_data = api.get(f'/contact/')
    return res_data['data']


def get_connected_accounts(conn):
    cursor = conn.execute("SELECT * FROM connected_accounts")
    return cursor.fetchall()


def check_email_already_send(conn, receiver_email) -> bool:
    cursor = conn.execute("SELECT * FROM emails WHERE receiver_email=?", (receiver_email,))
    if len(cursor.fetchall()) == 0:
        return False
    return True


def check_lead_availability(conn, lead_id) -> bool:
    cursor = conn.execute("SELECT * FROM leads WHERE lead_id=?", (lead_id,))
    if len(cursor.fetchall()) == 0:
        return False
    return True


def assign_timestamp_with_limit(connected_accounts: list) -> dict:
    data = {}
    for connected_account in connected_accounts:
        data[connected_account[2]] = {'timestamp': time.time(), 'limit': 0}
    return data


def update_timestamp_with_limit(connected_accounts_time_limits, sender_email) -> dict:
    timestamp, limit = connected_accounts_time_limits[sender_email]['timestamp'], \
        connected_accounts_time_limits[sender_email]['limit']
    connected_accounts_time_limits[sender_email] = {'timestamp': time.time() + 960, 'limit': limit + 1}
    return connected_accounts_time_limits


def check_any_connected_accounts_have_valid_limit(connected_accounts_time_limits) -> bool:
    for key in connected_accounts_time_limits:
        if connected_accounts_time_limits[key]['limit'] < 30:
            return True
    return False


def check_connected_account_availability(data: dict, connect_account_email: str) -> bool:
    try:
        if time.time() > data[connect_account_email]['timestamp'] and data[connect_account_email]['limit'] <= 30:
            return True
        return False
    except Exception as ex:
        return False


def run():
    logging.info('Script starts running ...')

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
    success_counter = 0

    # looping all the connected accounts to send email
    contacts_pointer = 0
    """ 
        Program will try to send email to all the contacts, if the limit of connect accounts exceed
        then run it next day. 
    """
    while contacts_pointer < total_contacts:

        # take a single contact to sent email
        while check_email_already_send(conn, contacts[contacts_pointer]['emails'][0]['email']) is True:
            contacts_pointer += 1
            logging.info(
                f"{contacts[contacts_pointer]['emails'][0]['email']} already receive an email, ignoring...")

        # check contact is available in DB
        while check_lead_availability(conn, contacts[contacts_pointer]['lead_id']) is False:
            logging.info(f"`{contacts[contacts_pointer]['lead_id']}` this lead id is not available in DB, ignoring...")
            time.sleep(2)
            contacts_pointer += 1

        # exit the script if all the available contacts receive email
        if contacts_pointer == total_contacts:
            logging.info('All the contacts receives email. Exiting the program.')
            exit()

        contact = contacts[contacts_pointer]

        """ 
            1st email will be sent from 1st connected account, 2nd from 2nd connected account and so on. 
            If the list in the DB is short and the emails need to repeat from the first email 
        """
        try:
            for connected_account in connected_accounts:

                # check whether the connected account is available to send email
                if check_connected_account_availability(connected_accounts_time_limits, connected_account[2]) is False:
                    logging.info(
                        f'{connected_account[2]} is not available to send email now, ignoring...')
                    continue

                # extract required data
                receiver_email = contact['emails'][0]['email']
                receiver_name = contact['name']
                contact_id = contact['id']
                lead_id = contact['lead_id']
                sender_name = connected_account[1]
                sender_email = connected_account[2]
                sender_pass = connected_account[3]  # required if email sent configured via Google
                reply_to = connected_account[5]  # will use if not null

                # make decision which service to use (close or gmail)
                if connected_account[4]:  # this connected account configured to send email via close

                    # generate payload to send email
                    payload = make_email_payload(contact_id, sender_name, sender_email, receiver_email, lead_id)

                    # send email via close
                    if send_email_via_close(api, payload) is True:
                        # create confirmation entry in email table
                        create_email_sent_confirmation(conn, sender_email, receiver_email, True,
                                                       date.today().strftime("%m/%d/%Y"))

                        # update the timestamp & limit for the used connected account
                        connected_accounts_time_limits = update_timestamp_with_limit(connected_accounts_time_limits,
                                                                                     sender_email)

                        # increase contacts pointer & success counter
                        contacts_pointer += 1
                        success_counter += 1

                        logging.info(f'--> Successfully sent email to {receiver_email} from {sender_email} vai close')

                    else:
                        logging.info(f'--> Failed to sent email {receiver_email} from {sender_email} vai close')

                else:  # this connected account configured to send email via Google

                    if send_email_via_google(sender_email, sender_pass, receiver_email, receiver_name,
                                             reply_to) is True:
                        # create confirmation entry in email table
                        create_email_sent_confirmation(conn, sender_email, receiver_email, False,
                                                       date.today().strftime("%m/%d/%Y"))

                        # update the timestamp & limit for the used connected account
                        connected_accounts_time_limits = update_timestamp_with_limit(connected_accounts_time_limits,
                                                                                     sender_email)

                        # increase contacts pointer & success counter
                        contacts_pointer += 1
                        success_counter += 1

                        logging.info(f'--> Successfully sent email to {receiver_email} from {sender_email} vai google')

                    else:
                        logging.info(f'--> Failed to sent email {receiver_email} from {sender_email} vai google')
        except Exception as e:
            pass

        # check whether all connected account reached their 30 emails per day limit
        if check_any_connected_accounts_have_valid_limit(connected_accounts_time_limits) is False:
            break

        """ wait 16 minutes to re-run the process, this will help to the program to use all the available connected 
            accounts under 30 days limit 
        """
        logging.info('waiting 16 minutes...')
        time.sleep(960)

    logging.info(f'total {success_counter} email have sent via this script.')
    logging.info('Script executed successfully!')


run()