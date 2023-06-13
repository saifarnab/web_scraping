from datetime import datetime

import pandas as pd
import pymysql

# db connection configuration
DATABASE_NAME = 'drug_bay'
HOST = 'localhost'
PORT = '3306'
USER = 'saif'
PASS = 'saif'
TXT_FILE_PATH = 'listings.txt'


def db_connection():
    # database connection
    conn = pymysql.connect(host=HOST, port=int(PORT), user=USER, passwd=PASS, database=DATABASE_NAME)
    cur = conn.cursor()
    return conn, cur


def read_txt() -> list:
    with open(TXT_FILE_PATH, "r") as file:
        return file.read().split('\n')


def db_insertion(conn, cur, data):

    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id, title, vendor_id, vendor, cat_id = fields[0], fields[1], fields[2], fields[3], fields[4]
            sub_cat_id, price, quantity, p_type, shipping_from = fields[5], fields[6], fields[7], fields[8], fields[9]
            shipping_to, des = fields[10], fields[11]

            price = 100 if price == '' else price
            quantity = 100 if quantity == '' else quantity

            product_sql = f"INSERT INTO products (id, name, description, rules, quantity, mesure, active, coins, category_id, " \
                          f"user_id, created_at, updated_at, types) VALUES('{listing_id}', '{title}', '{des}', 'No rules', " \
                          f"'{quantity}', '{price}', '1', 'btc', '{cat_id}','{vendor_id}', NOW(), NOW(), 'all')ON DUPLICATE" \
                          f" KEY UPDATE name = VALUES(name), description = VALUES(description), rules = VALUES(rules)," \
                          f" quantity = VALUES(quantity), mesure = VALUES(mesure), active = VALUES(active), coins = VALUES(coins)," \
                          f" category_id = VALUES(category_id), user_id = VALUES(user_id), created_at = VALUES(created_at)," \
                          f" updated_at = VALUES(updated_at), types = VALUES(types)"

            cur.execute(product_sql)
            conn.commit()

            # physical_sql = f"INSERT INTO physical_products (id, countries_option, countries, country_from, created_at," \
            #                f" updated_at) VALUES ('{listing_id}', 'all', ' ', '{shipping_from}', NOW(), NOW()) ON DUPLICATE " \
            #                f"KEY UPDATE countries_option=VALUES(countries_option), countries=VALUES(countries)," \
            #                f" country_from=VALUES(country_from), created_at=VALUES(created_at), updated_at=VALUES(updated_at)"
            # cur.execute(product_sql)
            # cur.execute(physical_sql)
            # conn.commit()
        except Exception as e:
            print(e)
            break



if __name__ == '__main__':
    connection, cursor = db_connection()
    lines = read_txt()
    db_insertion(connection, cursor, lines)
    connection.close()
