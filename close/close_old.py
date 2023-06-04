# import os
#
# from closeio_api import Client
# from core.src.instance.abstract import JobListing
# from core.src.instance.config import Config
# from core.src.instance.loggers import logger
# from core.src.io.read import read_listings_from_file
# from definitions import OUTPUT_DIRECTORY
#
# COMPANY_DESCRIPTION_ID = 'cf_1Ojv34J6JICroikPTpA7p688vXTdQN9sxk67NBVWPfF'
# COMPANY_LINKEDIN_ID = 'cf_4PA7FtCCanVzoatHEWSlBA5x3wrcbi3yPj9Sqxiwp0f'
# COMPANY_EMPLOYEE_COUNT_ID = 'cf_Bhd9bU7oEJNZflcvhNTtePHG19W7NsPOkDbFX3S7pMP'
#
# CONTACT_LINKEDIN_ID = 'cf_7F0p3Qt8YRTMHYp8XyPeFCMOpPzdIOpW0qdqQ5DWYQD'
# CONTACT_POSITION_ID = 'cf_EjGBqY7dy2vMm6bnpYgbn5KHUrpeb4fPqjD6J0Ju0b9'
# PENDING_STATUS_ID = 'stat_iqhy3Y2HGaKltd4nFEh77DWAv7zQOxuHE0zawknQJDA'
#
# client = Client(Config.CLOSE_API_KEY)
#
#
# def upload_listing_to_close(listing: JobListing) -> str:
#     company_url = listing.company.company_url if len(listing.company.company_url) else listing.company_url_linkedin
#
#     contact_name: str = " ".join([listing.person.contact_first_name, listing.person.contact_last_name])
#     contact_dict = {'name': contact_name,
#                     'phones': [{'type': 'office', 'phone': listing.person.contact_phone_number}],
#                     'emails': [{'type': 'office', 'email': listing.person.contact_email}],
#                     'status_id': PENDING_STATUS_ID,
#
#                     'custom.{}'.format(CONTACT_LINKEDIN_ID): listing.person.contact_linkedin_url,
#                     'custom.{}'.format(CONTACT_POSITION_ID): listing.person.contact_job_title}
#
#     city, state = listing.location.split(",") if len(listing.location) else ('N/A', 'N/A')
#     address_dict = {'label': 'business', 'city': city.strip(), 'state': state.strip(), 'country': 'US'}
#
#     payload = {'contacts': [contact_dict], 'name': listing.company.company_name.strip(), 'url': company_url,
#                'addresses': [address_dict]}
#
#     field_map = {COMPANY_DESCRIPTION_ID: listing.company.company_description,
#                  COMPANY_LINKEDIN_ID: listing.company_url_linkedin,
#                  COMPANY_EMPLOYEE_COUNT_ID: listing.company.company_size}
#
#     for k, v in field_map.items():
#         if len(v):
#             payload['custom.{}'.format(k)] = v
#
#     resp = client.post('lead', data.bson=payload)
#     logger.info("Lead created successfully : %s" % resp)
#
#     return resp['id']
#
#
# def add_activity_note(lead_id: str, note: str = 'Voice note created successfully'):
#     resp = client.post('activity/note', data.bson={"note": note, "lead_id": lead_id})
#     logger.info("Note response : %s" % str(resp))
#
#
# if __name__ == '__main__':
#
#     listings = read_listings_from_file(os.path.join(OUTPUT_DIRECTORY, 'sample_contacts.csv'))
#     sample_listing = listings[0]
#
#     logger.info("Sample listing : %s" % str(sample_listing))
#     lead_id = upload_listing_to_close(sample_listing)
#
#     add_activity_note(lead_id)
#
