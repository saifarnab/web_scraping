import csv
import random
import re
import subprocess
from os.path import basename
from PIL import Image

from bs4 import BeautifulSoup
import pandas as pd
import requests


def get_request_headers() -> dict:
    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/50.0.2661.102 Safari/537.36'}


def create_csv():
    with open(f'gym_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["title", "exercise_info", "exercise_img", "exercise_instruction", "benefits", "muscle_groups",
                 "equipment", "muscle_img", "muscle_worked"]
        writer.writerow(field)


def write_csv(row):
    with open(f'gym_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def run():
    create_csv()
    exercise_urls = [
        'https://fitnessprogramer.com/exercise-primary-muscle/neck/',
        'https://fitnessprogramer.com/exercise-primary-muscle/trapezius/',
        'https://fitnessprogramer.com/exercise-primary-muscle/shoulders/',
        'https://fitnessprogramer.com/exercise-primary-muscle/chest/',
        'https://fitnessprogramer.com/exercise-primary-muscle/back/',
        'https://fitnessprogramer.com/exercise-primary-muscle/erector-spinae/',
        'https://fitnessprogramer.com/exercise-primary-muscle/biceps/',
        'https://fitnessprogramer.com/exercise-primary-muscle/triceps/',
        'https://fitnessprogramer.com/exercise-primary-muscle/forearm/',
        'https://fitnessprogramer.com/exercise-primary-muscle/abs/',
        'https://fitnessprogramer.com/exercise-primary-muscle/leg/',
        'https://fitnessprogramer.com/exercise-primary-muscle/calf/',
        'https://fitnessprogramer.com/exercise-primary-muscle/hip/',
        'https://fitnessprogramer.com/exercise-primary-muscle/cardio/',
        'https://fitnessprogramer.com/exercise-primary-muscle/full-body/'
    ]

    for url in exercise_urls:
        page = requests.post(url, headers=get_request_headers())
        data = []
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            total_page = soup.findAll('span', class_='page')
            total_page = total_page[len(total_page) - 1].text
            details_pages = []
            for num in range(int(total_page)):
                page_url = f'{url}page{num + 1}/'
                new_page = requests.post(page_url, headers=get_request_headers())
                soup = BeautifulSoup(new_page.content, "html.parser")
                details_button = soup.findAll('a', class_='button', href=True)
                for each_details_button in details_button:
                    details_pages.append(each_details_button['href'])

            for ind_de, each_detail_page in enumerate(details_pages):
                details_page = requests.post(each_detail_page, headers=get_request_headers())
                soup = BeautifulSoup(details_page.content, "html.parser")
                title = soup.find('h1', class_='page_title').text.strip()
                vc_labels = soup.findAll('small', class_='vc_label')
                vc_bars = soup.findAll('span', class_='vc_bar')
                muscle_worked = {}
                for vc_label, vc_bar in zip(vc_labels, vc_bars):
                    muscle_worked[vc_label.text] = vc_bar['data-value'] + '%'

                muscle_worked = f'{muscle_worked}'
                if muscle_worked == '{}':
                    muscle_worked = ''

                print(f'{ind_de + 1} --> {each_detail_page} --> {title}')

                images = soup.findAll('img')
                if len(images) == 5:
                    exercise_img = images[1]['src']
                    muscle_img = images[3]['src']
                elif len(images) in [2, 3]:
                    exercise_img = images[1]['src']
                    muscle_img = ''
                elif len(images) == 4:
                    exercise_img = images[1]['src']
                    muscle_img = images[2]['src']
                else:
                    exercise_img = ''
                    muscle_img = ''

                if exercise_img != '':
                    with open(f'images/{exercise_img.split("/")[-1]}', "wb") as img:
                        img.write(requests.get(exercise_img).content)
                    exercise_img = f'/user/downloads/{exercise_img.split("/")[-1]}'

                if muscle_img != '':
                    with open(f'images/{muscle_img.split("/")[-1]}', "wb") as img:
                        img.write(requests.get(muscle_img).content)
                    muscle_img = f'/user/downloads/{muscle_img.split("/")[-1]}'

                try:
                    muscle_groups = ''
                    equipment = ''
                    groups_equipment = soup.findAll('div', class_='group-content')[1:]
                    for ind, item in enumerate(groups_equipment):
                        group_content_ul = item.findAll('li')
                        if ind == 0:
                            for li in group_content_ul:
                                muscle_groups += (li.text.replace('\n', '').strip() + ', ')
                        if ind == 1:
                            for li in group_content_ul:
                                equipment += (li.text.replace('\n', '').strip() + ', ')

                    muscle_groups = str({'primary': muscle_groups})

                    write_csv([title, '', exercise_img, '', '', muscle_groups, equipment, muscle_img, muscle_worked])

                except Exception as ex:
                    print(ex)

        # print(data)
        # df = pd.DataFrame(data, columns=["title", "exercise_info", "exercise_img", "exercise_instruction", "benefits",
        #                                  "muscle_groups", "equipment", "muscle_img", "muscle_worked"])
        # df.to_csv(f"data.csv", index=False, encoding='utf8')


run()
