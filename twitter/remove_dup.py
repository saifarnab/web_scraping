import logging


def check_duplicate(rows: list, row: str) -> bool:
    for item in rows:
        print(row)
        item = item.split(',')
        # row = row.split(',')
        if item[3] == row[3] and item[5] == row[5]:
            return True
    return False

def rename():
    df['First Season'].loc[(df['First Season'] > 1990)] = 1


def run():
    import pandas as pd
    df = pd.read_csv('data_6074.csv')
    df['Tweet_Number_of_Looks'] = 'N/A'


if __name__ == '__main__':
    logging.info('Script start running ...')
    run()
    logging.info(f'Script successfully executed!')
