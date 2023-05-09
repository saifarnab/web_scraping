import json

import requests

API_KEY = "67e8bf64-ca08-4df2-ab86-b62f0aa11f2d"


def scrapper():
    response = requests.get("https://api.cricapi.com/v1/matches?apikey=" + API_KEY + "&offset=100")
    text = json.dumps(response.json(), sort_keys=True, indent=4)
    data = json.loads(text)
    print(data['data'][0]['date'])
    print(data['data'][24]['date'])
    print("----------------------------Match List -----------------")
    # for value in data:
    #     print(" Name - " + value['name'] + "\n" + " status - " + value['status'] + "\n" + " venue -  " + value[
    #         'venue'] + "\n" + "dateTimeGMT - " + value['dateTimeGMT'] + "\n")


if __name__ == "__main__":
    scrapper()
