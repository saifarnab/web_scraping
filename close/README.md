# outbound-dev

// first you need to install Python modules:
pip install --upgrade -r requirements.txt

//Next you need to rename your Google API credentials file to"
"client_secrets.json"
https://pythonhosted.org/PyDrive/quickstart.html

//Change these variables according to your Google Drive folders IDs:
input_folder_id = 'GOOGLE_DRIVE_FOLDER_ID_HERE'
output_folder_id = 'GOOGLE_DRIVE_FOLDER_ID_HERE'
neverbounce_api_key = 'NEVERBOUNCE_API_KEY_HERE

//On the very first run the script will open the browser and ask you to allow the app to access your google drive

//After that it will save credentials in credentials.json file and use it on next runs (to refresh oAuth token)

//Expected output in the console
23:00:42 INFO file_cache is only supported with oauth2client<4.0.0
23:00:42 INFO Downloading 3-6-2023 Colorado Seamless List - 3-6-2023 Colorado Seamless List (1) Test.csv to local path [downloads\3-6-2023 Colorado Seamless List - 3-6-2023 Colorado Seamless List (1) Test.csv]...
23:00:44 INFO Generating emails for Neverbounce API...
23:01:41 INFO Waiting untill the job 15081481 is complete...
23:01:47 INFO Waiting untill the job 15081481 is complete...
23:01:53 INFO Waiting untill the job 15081481 is complete...
23:01:59 INFO Waiting untill the job 15081481 is complete...
23:02:05 INFO Waiting untill the job 15081481 is complete...
23:02:31 INFO Generating output file for upload: uploads\3-6-2023 Colorado Seamless List - 3-6-2023 Colorado Seamless List (1) Test.csv
23:02:31 INFO Uploading to Google Drive: uploads\3-6-2023 Colorado Seamless List - 3-6-2023 Colorado Seamless List (1) Test.csv
23:02:34 INFO Processing 3-6-2023 Colorado Seamless List - 3-6-2023 Colorado Seamless List (1) Test.csv COMPLETE!
23:02:34 INFO Downloading apollo-contacts-export (7) - apollo-contacts-export (7) (1).csv to local path [downloads\apollo-contacts-export (7) - apollo-contacts-export (7) (1).csv]...
23:02:35 INFO Generating emails for Neverbounce API...
23:02:38 INFO Waiting untill the job 15081490 is complete...
23:02:42 INFO Generating output file for upload: uploads\apollo-contacts-export (7) - apollo-contacts-export (7) (1).csv
23:02:42 INFO Uploading to Google Drive: uploads\apollo-contacts-export (7) - apollo-contacts-export (7) (1).csv
23:02:45 INFO Processing apollo-contacts-export (7) - apollo-contacts-export (7) (1).csv COMPLETE!
Done!
