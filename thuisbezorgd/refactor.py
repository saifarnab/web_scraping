import pandas as pd


def remove_duplicates():
    df = pd.read_csv('thu_data_home_2.csv')
    df = df.drop_duplicates()
    df.to_csv('8001-9999.csv', index=False)


def merge_csv():
    # Read the two CSV files into separate pandas DataFrames
    df1 = pd.read_csv('storage/5001-8000.csv',)
    df2 = pd.read_csv('storage/8001-9999.csv')
    merged_df = pd.concat([df1, df2], ignore_index=True)
    merged_df.to_csv('storage/5001-9999.csv', index=False)


if __name__ == "__main__":
    merge_csv()
