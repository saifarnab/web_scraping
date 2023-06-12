=============
Prerequisites
=============
1. Python 3.x - https://www.python.org/downloads/
2. Chromedriver (please refer to your Chrome browser version for compatibiltiy) - https://chromedriver.chromium.org/downloads
3. Place the chromedriver.exe in the same folder as the script.

=============
Install & Run
=============
1. Install Python modules used to run the scraper
$ pip3 install -r requirements.txt

2. Run the script (not in headless mode)
$ python3 run.py  --country england --league "premier league" --season 2021/2022


==========
HELP
==========

$ python run.py --help

usage: run.py [-h] --country COUNTRY --league LEAGUE [--season SEASON] [--linux LINUX] [--num_match NUM_MATCH]

Scrape Odds Portal Website

optional arguments:
  -h, --help            show this help message and exit
  --country COUNTRY     Country to select the leagues (i.e england)
  --league LEAGUE       League in the country (i.e premier league)
  --season SEASON       Season to scrape (i.e 2021/2022)
  --linux LINUX
  --num_match NUM_MATCH
                        Scrape only N matches

=====
BUGS
=====
Please contact the developer @ thewebscraper007@gmail.com
