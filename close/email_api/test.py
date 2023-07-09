from datetime import datetime
import pytz

def convert_timezone(datetime_str):
    # Parse the input datetime string
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S%z')

    # Define the source and destination timezones
    source_tz = pytz.timezone('UTC')
    destination_tz = pytz.timezone('America/Denver')

    # Convert the datetime object to the source timezone
    datetime_obj = datetime_obj.astimezone(source_tz)

    # Convert the datetime object to the destination timezone
    datetime_obj = datetime_obj.astimezone(destination_tz)

    # Format the datetime string in the destination timezone
    formatted_datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_datetime_str


datetime_str = '2023-07-06 14:41:36+03:00'
converted_datetime_str = convert_timezone(datetime_str)
print(converted_datetime_str)
