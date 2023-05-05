import subprocess
import gspread
from gspread_formatting import *
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# install dependencies
subprocess.check_call(['pip', 'install', 'pandas'])
subprocess.check_call(['pip', 'install', 'gspread'])
subprocess.check_call(['pip', 'install', 'oauth2client'])

# define google api credentials & scopes
credential = "pf-cloud-apis-995e6222b9da.json"
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def google_service_auth():
    cred = ServiceAccountCredentials.from_json_keyfile_name(credential, scopes=scopes)
    return gspread.authorize(cred)


def read_csv():
    return pd.read_csv("stock_data.csv")


def define_rule():
    rule = {
        'ranges': [
            {
                'sheetId': market_data.id,
                'startRowIndex': 1,  # start from row 2 to exclude header row
                'startColumnIndex': 11,  # apply to column K
                'endRowIndex': len(market_data.get_all_values()) + 1,  # end at the last row
                'endColumnIndex': 12,  # apply to column L
            }
        ],
        'booleanRule': {
            'condition': {
                'type': 'BOOLEAN',
                'values': [{'userEnteredValue': 'TRUE'}]
            },
            'format': {
                'backgroundColor': {
                    'red': 1.0,
                    'green': 0.498,
                    'blue': 0.0
                },
            }
        }
    }

    # Add the conditional formatting rule to the worksheet
    add_rule_request = {
        'addConditionalFormatRule': {
            'rule': rule,
        }
    }

    # Remove any existing conditional formatting rules for the same range
    delete_rule_request = {
        'deleteConditionalFormatRule': {
            'sheetId': market_data.id,
            'index': 0,  # delete the first rule (there should only be one rule)
            'rule': rule,
        }
    }

    return add_rule_request, delete_rule_request


def processor(idx):
    df = read_csv()
    for key, value in df.iterrows():
        temp = [value['Date'], value['Symbol'], value['CompanyName'], value['ClosingPrice'], value['FiftyDayAverage'],
                value['TwentyDayAverage'], value['FiftyDayAverageLast'], value['TwentyDayAverageLast'],
                # value['TwoHundredDayAverage'], value['TwoHundredTotalLastAverage'],
                f'=IF(AND((E{idx}-F{idx})>0,(E{idx}-F{idx})<(G{idx}-H{idx})),TRUE,FALSE)']

        market_data.insert_row(temp, idx, value_input_option='USER_ENTERED')
        idx += 1


if __name__ == "__main__":
    print("Starting script.....")

    # create google api client
    client = google_service_auth()

    # parse worksheet
    market_data = client.open('Stocks').worksheet('MarketData')

    # find the insertable row for market data
    next_available_row = len(list(filter(None, market_data.col_values(1)))) + 1

    print('------> process code being processed...')

    # push to spreadsheet
    processor(next_available_row)

    # define rule
    add_rule_request, delete_rule_request = define_rule()

    # market_data.batch_update([add_rule_request, delete_rule_request])

    print("All the data have been pushed to spreadsheet from stock_data.csv!!!!")
