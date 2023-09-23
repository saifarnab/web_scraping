import openpyxl
import pandas as pd


def check_data_exists():
    filename = 'files/atp_1.xlsx'
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in sheet.iter_rows(values_only=True):
        print(row[3])


def new_line_parser():
    file_path = 'files/wta_1.xlsx'  # Replace with the actual path to your Excel file
    df = pd.read_excel(file_path)

    # Function to remove newlines and handle NaN values
    def process_cell(cell_value):

        if pd.isna(cell_value):  # Check if the value is NaN
            return ''  # Replace NaN with an empty string
        else:
            return str(cell_value).replace('\n', '')

    # Apply the process_cell function to each cell in the DataFrame
    df = df.applymap(process_cell)

    # Save the processed DataFrame to a new Excel file
    output_file_path = 'files/new_wtp.xlsx'  # Replace with the desired output file path
    df.to_excel(output_file_path, index=False)

    print('Data processed and saved to', output_file_path)


new_line_parser()
