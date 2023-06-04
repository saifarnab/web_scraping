import copy

import pandas as pd
import pdfplumber


# def pdf_scraping():
# pdf = PDFQuery('coventry_hmo/coventry_p4-5.pdf')
# pdf.load()
#
# # Use CSS-like selectors to locate the elements
# text_elements = pdf.pq('LTTextLineHorizontal')
#
# # Extract the text from the elements
# text = [t.text for t in text_elements]
# test_list = [list(g) for k, g in groupby(text, lambda x: x == 'Licensee ') if not k]
#
# data.bson = []
# for index, item in enumerate(test_list):
#     item = [i.strip() for i in item]
#     item.insert(0, "Licensee")
#
#     for i, j in enumerate(item):
#         if j != '':
#             print(f"{i} -> {j}")
#
#     data.bson.append({
#         'date': item[10],
#         'reference': item[1]
#     })
#
#     print(item)

# reader = PdfReader("coventry_hmo/coventry_p4-5.pdf")
# number_of_pages = len(reader.pages)
# print(number_of_pages)
# page = reader.pages[0]
# text = page.extract_text()
# print(text)

# from pdfminer.high_level import extract_text
#
# text = extract_text("coventry_hmo/coventry_p4-5.pdf")
# text = text.strip()
# text = text.replace("\n", "")
# text = text.replace("\t", "")
# test_list = [list(g) for k, g in groupby(text, lambda x: x == "REGISTER") if not k]
# print(test_list)
#
# from pdfrw import PdfReader, PdfWriter, IndirectPdfDict
# x = PdfReader('coventry_hmo/coventry_p4-5.pdf')
# print(x.pages[0].Contents.stream)


def pdf_scraping() -> list:
    data = []
    with pdfplumber.open("conventry.pdf") as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text().split('\n')
            if text[0] == 'REGISTER OF HMO LICENCES':
                try:
                    date = text[1]
                except Exception as e:
                    date = ''

                address, ref, licensed_date, licensee, licensee_address, expiry_date, max_letting_units, \
                    max_occupants, house_holds, person, self_contained, non_self_contained, \
                    floors_from, living_accommodation, sleeping_accommodation, \
                    kitchens, bathroom_shower, sinks, toilets, terraced, managers_details = 'N/A', 'N/A', 'N/A', 'N/A',\
                    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', \
                    'N/A', 'N/A', 'N/A'

                for t_index, t_data in enumerate(text):
                    # print(f"{i} -> {t_index} -> {t_data}")

                    if 'Reference LN/' in t_data:
                        try:
                            temp = t_data.split('Reference LN/')
                            address = temp[0].strip()
                            ref = "LN/" + temp[1].strip()
                        except Exception as e:
                            pass

                    if 'Licensed Date' in t_data:
                        try:
                            licensed_date = t_data.split('Licensed Date')[1]
                        except Exception as e:
                            pass

                    if 'Licensee Address' in t_data:
                        try:
                            licensee_address = t_data.split('Licensee Address')[-1]
                        except Exception as e:
                            pass

                    elif 'Licensee' in t_data:
                        try:
                            licensee = t_data.split('Licensee')[-1]
                        except Exception as e:
                            pass

                    if 'Expiry Date' in t_data:
                        try:
                            expiry_date = t_data.split('Expiry Date')[1]
                        except Exception as e:
                            pass

                    if 'Max. Letting units' in t_data:
                        try:
                            max_letting_units = int(t_data.split('Max. Letting units')[1].strip().split(' ')[0])
                        except Exception as e:
                            max_letting_units = ''

                    if 'Max Occupants' in t_data:
                        try:
                            max_occupants = int(t_data.split('Max Occupants')[1].strip().split(' ')[0])
                        except Exception as e:
                            max_occupants = ''

                    if "Managers Details" in t_data:
                        try:
                            managers_details_temp = t_data.split("Managers Details")[1].strip()
                            if managers_details_temp not in ['Semi Detached', 'Detached', 'End Terraced', 'Terraced', 'Important infomation - please read.']:
                                managers_details = managers_details_temp
                            if text[t_index + 1] not in ['Semi Detached', 'Detached', 'End Terraced', 'Terraced', 'Important infomation - please read.']:
                                managers_details += text[t_index + 1]
                        except Exception as e:
                            pass

                    if 'Households' in t_data:
                        try:
                            house_holds = int(t_data.split('Households')[1].strip().split(' ')[0])
                        except Exception as e:
                            house_holds = ''

                    if 'Persons' in t_data:
                        try:
                            person = int(t_data.split('Persons')[1].strip().split(' ')[0])
                        except Exception as e:
                            person = ''

                    if 'Non- Self Contained' in t_data:
                        try:
                            non_self_contained = int(t_data.split('Non- Self Contained')[1].strip().split(' ')[0])
                        except Exception as e:
                            non_self_contained = ''

                    elif 'Self Contained' in t_data:
                        try:
                            self_contained = int(t_data.split('Self Contained')[1].strip().split(' ')[0])
                        except Exception as e:
                            self_contained = ''

                    if 'Floors From' in t_data:
                        try:
                            floors_from = int(t_data.split('Floors From')[1].strip().split(' ')[0])
                        except Exception as e:
                            floors_from = ''

                    if 'Living Accomodation' in t_data:
                        try:
                            living_accommodation = int(t_data.split('Living Accomodation')[1].strip().split(' ')[0])
                        except Exception as e:
                            living_accommodation = ''

                    if 'Sleeping Accomodation' in t_data:
                        try:
                            sleeping_accommodation = int(t_data.split('Sleeping Accomodation')[1].strip().split(' ')[0])
                        except Exception as e:
                            sleeping_accommodation = ''

                    if 'Bathrooms/Shower rooms' in t_data:
                        try:
                            bathroom_shower = int(t_data.split('Bathrooms/Shower rooms')[1].strip().split(' ')[0])
                            terraced = t_data.split('Bathrooms/Shower rooms')[0].strip()
                            if 'to' in terraced:
                                terraced = "Converted from Residential " + terraced
                            elif 'N/A' in terraced:
                                terraced = ''
                        except Exception as e:
                            bathroom_shower = ''

                    if 'Toilets with Wash Basins' in t_data:
                        try:
                            toilets = int(t_data.split('Toilets with Wash Basins')[1].strip().split(' ')[0])
                        except Exception as e:
                            toilets = ''

                    if 'Kitchens' in t_data:
                        try:
                            kitchens = int(t_data.split('Kitchens')[1].strip().split(' ')[0])
                        except Exception as e:
                            kitchens = ''

                    if 'Sinks' in t_data:
                        try:
                            sinks = int(t_data.split('Sinks')[1].strip().split(' ')[0])
                        except Exception as e:
                            sinks = ''
                print(f"Extracted data from page = {i+1}")
                if ref != 'N/A':
                    data.append(
                        [i + 1, date, ref, "", licensee, licensee_address, address, managers_details, licensed_date, expiry_date,
                         max_letting_units, max_occupants, house_holds, person, terraced, self_contained,
                         non_self_contained, floors_from, living_accommodation, sleeping_accommodation,
                         bathroom_shower, toilets, kitchens, sinks])

    return data


if __name__ == '__main__':
    data = pdf_scraping()
    columns = ['Page', 'Date', 'Reference', 'HMO Landlords', 'Licensee Name', 'Licensee Address', 'Address',
               'Managers Details', 'Licensee Date', 'Expiry Date', 'Max. Letting units', 'Max Occupants',
               'Households', 'Persons', 'Terraced', 'Self Contained', 'Non- Self Contained', 'Floors From',
               'Living Accommodation', 'Sleeping Accommodation', 'Bathrooms/Shower rooms', 'Toilets with Wash Basins',
               'Kitchens', 'Sinks']
    df = pd.DataFrame(data, columns=columns)
    sorted_df = df.sort_values(by=['Licensee Name', 'Licensee Address'], ascending=True)
    sorted_df.to_excel(f"coventry_hmo/data_re_gen.xlsx", index=False)
