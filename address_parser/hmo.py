import pandas as pd


def split_address_and_create_excel(input_file_path, output_file_path):
    def strip_and_handle_none(value):
        if isinstance(value, str):
            return value.strip()
        return value

    try:
        # Read the original Excel file into a pandas DataFrame
        df = pd.read_excel(input_file_path)

        # Split the 'Licensee Address - Company name (NEEDS SPLITTING)' column into separate columns
        split_data = df['Address'].str.split(',', expand=True)

        # Remove any empty strings or None values from the split data
        split_data = split_data.applymap(lambda x: strip_and_handle_none(x) if isinstance(x, str) else x)

        # Get the actual address length (number of non-empty address lines)
        actual_address_length = split_data.apply(lambda row: row.dropna().shape[0], axis=1)

        # Create new columns with the cleaned split data
        address_line_columns = []
        for i in range(actual_address_length.max()):
            col_name = f'Licensee Address_line_{i + 1}'
            df[col_name] = split_data[i]
            address_line_columns.append(col_name)

        # Extract the postal code from the last non-empty element of each row
        df['Licensee_postal_code'] = split_data.apply(
            lambda x: x.dropna().iloc[-1].strip() if len(x.dropna()) > 0 else '', axis=1)

        # Check if the Licensee_postal_code matches any of the address line columns and make that column empty
        for col in address_line_columns:
            df.loc[df['Licensee_postal_code'] == df[col], col] = ''

        # Write the DataFrame with additional columns to a new Excel file
        df.to_excel(output_file_path, index=False)

        print(f"Successfully created a new Excel file with split address at '{output_file_path}'.")
    except FileNotFoundError:
        print(f"Error: File '{input_file_path}' not found.")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")


def run():
    input_file_path = "CoventryHMO.xlsx"
    output_file_path = "CoventryHMO_v2.xlsx"
    split_address_and_create_excel(input_file_path, output_file_path)


if __name__ == '__main__':
    run()
