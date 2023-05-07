# import requests
# from bs4 import BeautifulSoup
# from openpyxl import load_workbook
# import time
# import re
#
# # Set your Scraper API key
# api_key = 'API KEY'
#
# # Load the Excel workbook
# wb = load_workbook('C:\\Users\\kyled\\OneDrive\\Desktop\\Script\\Testing\\realtor Scrape.xlsx')
#
# # Select the active worksheet
# ws = wb.active
#
# # Define the starting row for the data
# row = 2
#
# ws.cell(row=1, column=4, value="Phone #1")
# ws.cell(row=1, column=5, value="Phone #2")
# ws.cell(row=1, column=6, value="Phone #3")
#
# # Loop through the URLs in column C and scrape the data
# for cell in ws['C'][1:]:
# # Get the URL from the cell value
#     url = cell.value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
# page_url = f'https://api.scraperapi.com/?api_key=c333d3ec36f9c6e6d5c7969de4bb1695&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Check if the URL is None
# if url is None:
#     break
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(5)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=row, column=4, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=row, column=4, value=phone_numbers[0])
# else:
#     ws.cell(row=row, column=4, value='No telephone number found')
#
# # Increment the row counter
# row += 1
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Loop through the rows and search for phone numbers again in rows where "No telephone number found" was initially written
# for cell in ws['D'][1:]:
# # Get the value in the cell
# value = cell.value
#
# # Check if the cell value is "No telephone number found"
# if value == 'No telephone number found':
# # Get the URL from the previous column
# url = ws.cell(row=cell.row, column=3).value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(10)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=cell.row, column=5, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=cell.row, column=5, value=phone_numbers[0])
# else:
#     ws.cell(row=cell.row, column=5, value='No telephone number found')
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Loop through the rows and search for phone numbers again in rows where "No telephone number found" was initially written
# for cell in ws['E'][1:]:
# # Get the value in the cell
# value = cell.value
#
# # Check if the cell value is "No telephone number found"
# if value == 'No telephone number found':
# # Get the URL from the previous column
# url = ws.cell(row=cell.row, column=3).value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(20)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=cell.row, column=6, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=cell.row, column=6, value=phone_numbers[0])
# else:
#     ws.cell(row=cell.row, column=6, value='No telephone number found')
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Save the updated Excel workbook
# wb.save('C:\\Users\\kyled\\OneDrive\\Desktop\\Script\\Testing\\realtor Scrape.xlsx')
#
# import requests
# from bs4 import BeautifulSoup
# from openpyxl import load_workbook
# import time
# import re
#
# # Set your Scraper API key
# api_key = 'API KEY'
#
# # Load the Excel workbook
# wb = load_workbook('C:\\Users\\kyled\\OneDrive\\Desktop\\Script\\Testing\\realtor Scrape.xlsx')
#
# # Select the active worksheet
# ws = wb.active
#
# # Define the starting row for the data
# row = 2
#
# ws.cell(row=1, column=4, value="Phone #1")
# ws.cell(row=1, column=5, value="Phone #2")
# ws.cell(row=1, column=6, value="Phone #3")
#
# # Loop through the URLs in column C and scrape the data
# for cell in ws['C'][1:]:
# # Get the URL from the cell value
# url = cell.value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Check if the URL is None
# if url is None:
#     break
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(5)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=row, column=4, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=row, column=4, value=phone_numbers[0])
# else:
#     ws.cell(row=row, column=4, value='No telephone number found')
#
# # Increment the row counter
# row += 1
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Loop through the rows and search for phone numbers again in rows where "No telephone number found" was initially written
# for cell in ws['D'][1:]:
# # Get the value in the cell
# value = cell.value
#
# # Check if the cell value is "No telephone number found"
# if value == 'No telephone number found':
# # Get the URL from the previous column
# url = ws.cell(row=cell.row, column=3).value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(10)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=cell.row, column=5, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=cell.row, column=5, value=phone_numbers[0])
# else:
#     ws.cell(row=cell.row, column=5, value='No telephone number found')
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Loop through the rows and search for phone numbers again in rows where "No telephone number found" was initially written
# for cell in ws['E'][1:]:
# # Get the value in the cell
# value = cell.value
#
# # Check if the cell value is "No telephone number found"
# if value == 'No telephone number found':
# # Get the URL from the previous column
# url = ws.cell(row=cell.row, column=3).value
#
# # Generate the API URL for scraping
# api_url = f'https://api.scraperapi.com/?api_key={api_key}&url={url}'
#
# # Make a GET request to the API
# response = requests.get(api_url)
#
# # Wait for 5 seconds before parsing the HTML content with BeautifulSoup
# time.sleep(20)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the telephone number link
# tel_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
#
# # Extract phone numbers from page text
# text = soup.get_text()
# phone_numbers = re.findall(r'\(\d{3}\) \d{3}-\d{4}', text)
#
# # Write the data to the worksheet
# if tel_link:
#     ws.cell(row=cell.row, column=6, value=tel_link['href'])
# elif phone_numbers:
#     ws.cell(row=cell.row, column=6, value=phone_numbers[0])
# else:
#     ws.cell(row=cell.row, column=6, value='No telephone number found')
#
# # Print the status code
# print(f'{url}: {response.status_code}')
#
# # Save the updated Excel workbook
# wb.save('C:\\Users\\kyled\\OneDrive\\Desktop\\Script\\Testing\\realtor Scrape.xlsx')
#
# import requests
# from bs4 import BeautifulSoup
# from openpyxl import Workbook
# from openpyxl.utils import get_column_letter
# from openpyxl.styles import Font, Alignment
# from openpyxl.worksheet.hyperlink import Hyperlink
# import tkinter as tk
#
# api_key = 'c333d3ec36f9c6e6d5c7969de4bb1695'
# zip_code = '33312'
# num_bedrooms = 2
# num_bathrooms = 2
# min_price = 'na'
# max_price = 2350
#
# v = 'https://www.realtor.com/apartments/33312/beds-2/baths-2/price-na-2350'
#
# url = f'https://api.scraperapi.com/?api_key={api_key}&url=https://www.realtor.com/apartments/{zip_code}/beds-{num_bedrooms}/baths-{num_bathrooms}/price-{min_price}-{max_price}'
#
# response = requests.get(url)
#
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, 'html.parser')
# addresses = soup.select('.card-address')
# prices = soup.select('.card-price')
# links = soup.select('.card-anchor[href]')
# wb = Workbook()
# ws = wb.active
# ws.title = "Addresses and Prices"
# ws.cell(row=1, column=1, value="Address")
# ws.cell(row=1, column=2, value="Price")
# ws.cell(row=1, column=3, value="Link")
# row = 2  # initialize the row counter variable
# for i, address in enumerate(addresses):
#     ws.cell(row=row, column=1, value=address.text.strip() + " ")
# row += 1  # increment the row counter variable
# row = 2  # reset the row counter variable
# for i, price in enumerate(prices):
#     ws.cell(row=row, column=2, value=price.text.strip())
# row += 1  # increment the row counter variable
# row = 2  # reset the row counter variable
# for link in links:
#     relative_url = link['href']
# absolute_url = f"https://www.realtor.com{relative_url}"
# ws.cell(row=row, column=3, value=absolute_url)
# ws.cell(row=row, column=3).hyperlink = absolute_url
# ws.cell(row=row, column=3).font = Font(underline='single', color='0563C1')
# ws.cell(row=row, column=3).alignment = Alignment(horizontal='left')
# row += 1  # increment the row counter variable
#
# wb.save("Realtor Scrape.xlsx")
