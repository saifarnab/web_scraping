import numpy as np
import pandas as pd

df = pd.read_csv('gym_data.csv')
df = df.fillna('')

# new = '<div>' + item.replace('\n', '</p><p>') + '</div>'
data = []

for index, row in df.iterrows():
    if row['exercise_info'] != '':
        exercise_info = '<ul><li>' + row['exercise_info'].replace('\n', '</li><li>') + '</li></ul>'
    else:
        exercise_info = ''
    if row['how_to'] != '':
        how_to = '<ul><li>' + row['how_to'].replace('\n', '</li><li>') + '</li></ul>'
    else:
        how_to = ''
    if row['benefits'] != '':
        benefits = '<ul><li>' + row['benefits'].replace('\n', '</li><li>') + '</li></ul>'
    else:
        benefits = ''

    data.append([row['title'], exercise_info, row['exercise_img'], how_to, benefits, row['muscle_groups'],
                 row['equipment'], row['muscle_img'], row['muscle_worked']])

df = pd.DataFrame(data, columns=["title", "exercise_info", "exercise_img", "exercise_instruction", "benefits",
                                 "muscle_groups", "equipment", "muscle_img", "muscle_worked"])
df.to_csv(f"new_gym_data.csv", index=False, encoding='utf8')