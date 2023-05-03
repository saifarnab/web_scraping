import pandas as pd
import pymysql

# database connection
connection = pymysql.connect(host="localhost", port=3306, user="admin", passwd="admin", database="gym")
print(connection)
cursor = connection.cursor()

df = pd.read_csv('new_gym_data.csv')
df = df.fillna('')

for index, row in df.iterrows():
    sql = "INSERT INTO exercises (`exercise_title`, `exercise_information`, `exercise_image`, `exercise_instructions`, `exercise_benefits`, `muscle_groups`, `equipment`, `muscle_image`, `muscle_worked`) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (row['title'], row['exercise_info'], row['exercise_img'], row['exercise_instruction'], row['benefits'],
           row['muscle_groups'], row['equipment'], row['muscle_img'], row['muscle_worked'])
    cursor.execute(sql, val)
    connection.commit()

connection.close()
