import pandas as pd


def remove_duplicates():
    df = pd.read_csv('storage/5001-9999.csv')
    df = df.drop_duplicates()
    df.to_csv('5001-9999-rd.csv', index=False)


def remove_duplicates2():
    df = pd.read_csv('storage/1016-9999.csv')
    columns_to_check = ['Name', 'Address', 'Opening Times', 'Categories', 'Rating', 'Delivery Time', 'Delivery Cost',
                        'Minimum Order', 'Product Url']
    df.drop_duplicates(subset=columns_to_check, inplace=True)
    df.to_csv('1016-9999-unique.csv', index=False)


def merge_csv():
    # Read the two CSV files into separate pandas DataFrames
    df1 = pd.read_csv('storage/1016-5000.csv', )
    df2 = pd.read_csv('storage/5001-9999.csv')
    merged_df = pd.concat([df1, df2], ignore_index=True)
    merged_df.to_csv('storage/1016-9999.csv', index=False)


def replace_value():
    data_frame = pd.read_csv('fix.csv')
    old_value = 'nan'
    new_value = ''
    for column in data_frame.columns:
        data_frame[column] = data_frame[column].replace(old_value, new_value)
    data_frame.to_csv('modified_fix.csv', index=False)


if __name__ == "__main__":
    merge_csv()
