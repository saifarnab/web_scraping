import logging


def check_duplicate(rows: list, row: str) -> bool:
    for item in rows:
        print(row)
        item = item.split(',')
        # row = row.split(',')
        if item[3] == row[3] and item[5] == row[5]:
            return True
    return False


def run():
    import pandas as pd
    toclean = pd.read_csv('data_6074.csv')
    deduped = toclean.drop_duplicates(['Author_Name', 'Tweet_Timestamp'])
    deduped.to_csv('data_6075.csv')


if __name__ == '__main__':
    logging.info('Script start running ...')
    run()
    logging.info(f'Script successfully executed!')
