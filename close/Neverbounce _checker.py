import csv
import os
import time
import json
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import neverbounce_sdk
import logging


def generate_emails(filename):
    logging.info('Generating emails for Neverbounce API...')
    emails = []
    email_field = ''
    if 'seamless' in filename.lower():
        email_field = 'Email 1'
    elif 'apollo' in filename.lower():
        email_field = 'Email'

    unique_emails = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row[email_field].strip()
            if email and email not in unique_emails:
                emails.append({'email': email})
                unique_emails[email] = 1
    return emails


def process_csv_using_neverbounce(filename, api_key, source_csv_filename):
    emails = generate_emails(filename)
    valid_emails = {}
    if emails:
        client = neverbounce_sdk.client(api_key=api_key, timeout=30)
        job = client.jobs_create(emails, filename=source_csv_filename)
        resp = client.jobs_parse(job['job_id'], auto_start=True)
        assert resp['status'] == 'success'

        # client.jobs_start(job['job_id'])
        while True:
            progress = client.jobs_status(job['job_id'])
            logging.info(
                f'Waiting untill the job {job["job_id"]} is complete... {progress["percent_complete"]} percent completed.')
            if progress['job_status'] == 'complete':
                break
            time.sleep(api_result_check_delay)

        results = client.jobs_results(job['job_id'])
        while True:
            logging.debug(f'Processing API response page #{results.page}...')
            for result in results.data['results']:
                email = result['data.bson']['email']
                status = result['verification']['result']
                if status == 'valid':
                    valid_emails[email] = 1
            if results.page < results.total_pages:
                results.get_next_page()
            else:
                break

    return valid_emails


def get_csv_type(filename):
    csv_type = None
    if 'seamless' in filename.lower():
        csv_type = 'seamless'
    elif 'apollo' in filename.lower():
        csv_type = 'apollo'
    return csv_type


def get_output_csv_fiedls_config(csv_type, output_fields_config_file):
    output_fields = []
    with open(output_fields_config_file, 'r', encoding='utf-8') as f:
        fields = json.load(f)
        if csv_type in fields:
            output_fields = fields[csv_type]
    return output_fields


def save_record(row, fields, writer):
    record = {}
    for field in fields:
        record[field['name']] = row[field['source_field']]
    writer.writerow(record)


def upload_file(upload_file_path, title, output_folder_id, drive):
    file1 = drive.CreateFile(
        {'title': title, 'parents': [{'id': output_folder_id}], })
    file1.SetContentFile(upload_file_path)
    file1.Upload()


# API Settings section
# Input folder will contain all the unprocessed/unverified CSVs
input_folder_id = '1dhPsK7RWirrgkzjv8HMx4zO1NH6_Av-j'
# Output folder will contain the processed files from Neverbounce
output_folder_id = '15kl8jFfBfwckU12hZnJxnIaa4epdBabw'
neverbounce_api_key = 'private_603ec623b35d2615df7a7c1a52e854f7'
downloads_folder = 'downloads'
uploads_folder = 'uploads'
output_fields_config_file = 'OutputFields.json'
api_result_check_delay = 5  # seconds

logging.basicConfig(
    # filename=log_file,
    # filemode='a',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

if not os.path.exists(downloads_folder):
    os.mkdir(downloads_folder)
if not os.path.exists(uploads_folder):
    os.mkdir(uploads_folder)

gauth = GoogleAuth()
# Create GoogleDrive instance with authenticated GoogleAuth instance
drive = GoogleDrive(gauth)

# get all files in the target folder
google_drive_csv_files = drive.ListFile(
    {'q': f"'{input_folder_id}' in parents and trashed=false"}).GetList()
for csv_file in google_drive_csv_files:
    try:
        csv_file_title = csv_file['title']
        local_path = os.path.join(downloads_folder, csv_file_title)
        logging.info(
            f'Downloading {csv_file_title} to local path [{local_path}]...')
        csv_file.GetContentFile(local_path)

        valid_emails = process_csv_using_neverbounce(
            local_path, neverbounce_api_key, csv_file_title)
        csv_type = get_csv_type(local_path)
        output_csv_fields_config = get_output_csv_fiedls_config(
            csv_type, output_fields_config_file)
        output_csv_fields = [field['name']
                             for field in output_csv_fields_config['fields']]

        upload_file_path = os.path.join(uploads_folder, csv_file_title)
        logging.info(f'Generating output file for upload: {upload_file_path}')
        with open(upload_file_path, 'w', encoding='utf-8') as f_out:
            writer = csv.DictWriter(
                f_out, fieldnames=output_csv_fields, lineterminator='\n')
            writer.writeheader()
            with open(local_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row[output_csv_fields_config['email']]
                    if email in valid_emails:
                        save_record(
                            row, output_csv_fields_config['fields'], writer)
        logging.info(f'Uploading to Google Drive: {upload_file_path}')
        upload_file(upload_file_path, csv_file_title, output_folder_id, drive)
        os.remove(local_path)
        os.remove(upload_file_path)
        csv_file.Delete()
        logging.info(f'Processing {csv_file_title} COMPLETE!')
    except Exception as e:
        error = str(e)
        logging.error(f'Error processing {csv_file_title}! {error}')

print('Done!')
