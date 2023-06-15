import random
import time

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
    # products table
    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id, title, vendor_id, vendor, cat_id = fields[0], fields[1], fields[2], fields[3], fields[4]
            sub_cat_id, price, quantity, p_type, shipping_from = fields[5], fields[6], fields[7], fields[8], fields[9]
            shipping_to, des = fields[10], fields[11]

            quantity = quantity.replace(',', '')
            price = 100 if price == '' else price
            quantity = 100 if quantity == '' else quantity
            title = title.replace('\"', '\'')
            des = des.replace('\"', '\'')

            if float(quantity) > 2147483647:
                quantity = 2147483647
            if len(title) > 100:
                title = title[:100]

            product_sql = f'INSERT INTO products (id, name, description, rules, quantity, mesure, active, coins, category_id, ' \
                          f'user_id, created_at, updated_at, types) VALUES("{listing_id}", "{title}", "{des}", "No rules", ' \
                          f'"{quantity}", "{price}", "1", "btc", "{cat_id}","{vendor_id}", NOW(), NOW(), "all")ON DUPLICATE' \
                          f' KEY UPDATE name = VALUES(name), description = VALUES(description), rules = VALUES(rules),' \
                          f'quantity = VALUES(quantity), mesure = VALUES(mesure), active = VALUES(active), coins = VALUES(coins),' \
                          f'category_id = VALUES(category_id), user_id = VALUES(user_id), created_at = VALUES(created_at),' \
                          f'updated_at = VALUES(updated_at), types = VALUES(types)'

            cur.execute(product_sql)
        except Exception as e:
            pass

    conn.commit()
    print('Execution in product table done.')

    # physical products table
    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id, shipping_from = fields[0], fields[9]

            physical_sql = f"INSERT INTO physical_products (id, countries_option, countries, country_from, created_at," \
                           f" updated_at) VALUES ('{listing_id}', 'all', ' ', '{shipping_from}', NOW(), NOW()) ON DUPLICATE " \
                           f"KEY UPDATE countries_option=VALUES(countries_option), countries=VALUES(countries)," \
                           f" country_from=VALUES(country_from), created_at=VALUES(created_at), updated_at=VALUES(updated_at)"
            cur.execute(physical_sql)
        except Exception as e:
            pass

    conn.commit()
    print('Execution in physical product table done.')

    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id = fields[0]
            images_sql = f"INSERT INTO images (id, product_id, image, first, created_at, updated_at) " \
                         f"VALUES ('{listing_id}', '{listing_id}', ' ', 0, NOW(), NOW()) ON DUPLICATE KEY UPDATE " \
                         f"product_id=VALUES(product_id), image=VALUES(image), first=VALUES(first), " \
                         f"created_at=VALUES(created_at), updated_at=VALUES(updated_at)"
            cur.execute(images_sql)
        except Exception as e:
            pass

    conn.commit()
    print('Execution in images table done.')

    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id, price = fields[0], fields[6]
            price = price.replace(',', '')
            price = 100 if price == '' else price
            offers_sql = f"INSERT INTO offers (id, product_id, min_quantity, price, created_at, updated_at)" \
                         f" VALUES ('{listing_id}', '{listing_id}', 1, '{price}', NOW(), NOW()) ON DUPLICATE " \
                         f"KEY UPDATE product_id=VALUES(product_id), min_quantity=VALUES(min_quantity)," \
                         f" price=VALUES(price), created_at=VALUES(created_at), updated_at=VALUES(updated_at)"
            cur.execute(offers_sql)
        except Exception as e:
            pass

    conn.commit()
    print('Execution in offers table done.')

    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            listing_id, title, price, quantity = fields[0], fields[1], fields[6], fields[7]
            title = title.replace('\"', '\'')
            price = price.replace(',', '')
            price = 100 if price == '' else price
            quantity = quantity.replace(',', '')
            quantity = 100 if quantity == '' else quantity
            quantity = int(float(quantity))
            price = float(price)

            if float(quantity) > 2147483647:
                quantity = 2147483647
            if len(title) > 255:
                title = title[:255]

            if price > 9999999:
                price = 9999999

            shipping_sql = f'INSERT INTO shippings (id, product_id, name, price, duration, from_quantity, to_quantity,' \
                           f'created_at, updated_at) VALUES ("{listing_id}", "{listing_id}", "{title}", {price},' \
                           f'"24 hours", 1, "{quantity}", NOW(), NOW()) ON DUPLICATE KEY UPDATE ' \
                           f'product_id=VALUES(product_id), name=VALUES(name), price=VALUES(price), duration=VALUES(duration),' \
                           f' from_quantity=VALUES(from_quantity), to_quantity=VALUES(to_quantity), ' \
                           f'created_at=VALUES(created_at), updated_at=VALUES(updated_at)'
            cur.execute(shipping_sql)
        except Exception as e:
            if not e.__str__().startswith('(1452'):
               pass

    conn.commit()
    print('Execution in shipping table done.')

    profile_bgs = [
        'profile-bg-weave',
        'profile-bg-stairs',
        'profile-bg-arrows',
        'profile-bg-zigzag',
        'profile-bg-carbon',
        'profile-bg-cross',
        'profile-bg-paper',
        'profile-bg-waves',
        'profile-bg-tablecloth',
        'profile-bg-seigaiha',
        'profile-bg-jcubes',
        'profile-bg-bricks',
        'profile-bg-checkerboard',
        'profile-bg-starrynight',
        'profile-bg-stars',
        'profile-bg-wave',
        'profile-bg-blueprint'
    ]

    levels = {
        1: 0,
        2: 30000,
        3: 60000,
        4: 90000,
        5: 180000,
        6: 360000,
        7: 720000,
        8: 1500000,
    }

    for idx, item in enumerate(data):
        if len(item) < 1:
            continue
        try:
            fields = str(item).split(':')
            vendor_id = fields[2]
            v_level = random.randint(1, 8)
            exp = levels[v_level]
            profile_bg = profile_bgs[random.randint(0, len(profile_bgs) - 1)]
            trusted = random.randint(0, 1)

            vendor_sql = f"INSERT INTO vendors (id, vendor_level, experience, about, profilebg, trusted, created_at," \
                         f" updated_at) VALUES ('{vendor_id}', {v_level}, {exp}, '', '{profile_bg}', " \
                         f"{trusted}, NOW(), NOW()) ON DUPLICATE KEY UPDATE vendor_level=VALUES(vendor_level), " \
                         f"experience=VALUES(experience), about=VALUES(about), profilebg=VALUES(profilebg)," \
                         f" trusted=VALUES(trusted), created_at=VALUES(created_at), updated_at=VALUES(updated_at)"
            cur.execute(vendor_sql)
        except Exception as e:
            pass

    conn.commit()
    print('Execution in vendors table done.')


if __name__ == '__main__':
    print('Script starts ...')
    connection, cursor = db_connection()
    lines = read_txt()
    db_insertion(connection, cursor, lines)
    connection.close()
