from datetime import datetime, timezone
from lxml import html
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

import time
import requests


class OddsPortalScraper:
    def __init__(self, chromedriver):
        self.driver = None
        self.binary = chromedriver
        self.table_tabs = ["1X2", "Home/Away", "Draw No Bet", "DNB",
                           "Double Chance", "Odd or Even", "Both Teams to Score"]
        self.div_tabs = ["Asian Handicap", "AH",
                         "Over/Under", "OU", "O/U", "European Handicap", "EH"]

        self.other_tabs = ["Correct Score", "Half Time / Full Time"]
        self.setup_chromedriver()

    def setup_chromedriver(self):
        options = Options()
        options.headless = True
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
        options.add_argument(f'user-agent={ua}')

        service = Service(str(Path(self.binary).resolve()))
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_window_size(1024, 600)
        self.driver.maximize_window()

    def get_matches(self, url, referer):
        try:
            cookies = {
                'XSRF-TOKEN': 'eyJpdiI6ImV3dFl6K2NhZGRWZVN5djBrK3VmWmc9PSIsInZhbHVlIjoiMUw1SytFaEZDSXZ6NXk5dTh6bnZnbURXU2YzT2FFMlN5N2M0UTZRczlVeFhHdW13bU5XS3VQWlZ3QU5YYlYrUmZZcW1Id0VpOXJnQnlqb2h3aE83ME14S1A1cVU1am1MVSt0QkFuaWpQdGJRWWJUOHVDNzJieEF3ZUNMaDBJZloiLCJtYWMiOiJjYjZmZDY5YTQ3OWQ0OTVkYTE4Y2I0MmFiNDViZTEzYTM0ZjFmYjMwY2UxZTJhMGEyOTJiYWVkN2E4MWMxMTYwIiwidGFnIjoiIn0%3D'
            }

            headers = {
                'authority': 'www.oddsportal.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'content-type': 'application/json',
                'referer': referer,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'x-xsrf-token': 'eyJpdiI6ImV3dFl6K2NhZGRWZVN5djBrK3VmWmc9PSIsInZhbHVlIjoiMUw1SytFaEZDSXZ6NXk5dTh6bnZnbURXU2YzT2FFMlN5N2M0UTZRczlVeFhHdW13bU5XS3VQWlZ3QU5YYlYrUmZZcW1Id0VpOXJnQnlqb2h3aE83ME14S1A1cVU1am1MVSt0QkFuaWpQdGJRWWJUOHVDNzJieEF3ZUNMaDBJZloiLCJtYWMiOiJjYjZmZDY5YTQ3OWQ0OTVkYTE4Y2I0MmFiNDViZTEzYTM0ZjFmYjMwY2UxZTJhMGEyOTJiYWVkN2E4MWMxMTYwIiwidGFnIjoiIn0='
            }

            response = requests.get(url, cookies=cookies, headers=headers)

            data = response.json()

            match_links = {}
            for row in data['d']['rows']:
                match = f"{row['home-name']} – {row['away-name']}"
                match_links[match] = f"https://www.oddsportal.com{row['url']}"

            return match_links

        except Exception as e:
            print(e)

    def extract_odds_data(self, url, match):
        driver = self.driver
        driver.get(url)

        data = {}
        actions = ActionChains(driver)
        wait = WebDriverWait(driver, 20)

        try:
            data.update({"Match": match})

            date = ""
            try:
                # Scrape match date
                date_element = driver.find_element(
                    By.XPATH, "//main/div[2]/div[3]/div[2]/div[1]/div[last()]")
                date = date_element.text.split(",")[1]

            except Exception as e:
                pass

            data.update({"Date": date})

            ht_score, at_score = "", ""
            try:
                match_result = driver.find_element(
                    By.XPATH, "//main/div[2]/div[3]/div[1]")

                # Scrape final score
                ht_score = match_result.find_element(
                    By.XPATH, "div[1]/div/div[last()]").text
                at_score = match_result.find_element(
                    By.XPATH, "div[3]/div/div[last()]").text

            except Exception as e:
                pass

            data.update({
                "Home Team Goals": ht_score,
                "Away Team Goals": at_score
            })

            # Copy "–" separator directly from website
            ht, at = match.split("–")
            data.update({
                "Home Team": ht,
                "Away Team": at
            })

            table = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'prio-odds')]/div"))
            )

            # Exclude last tab (for "more links")
            tabs = table.find_elements(By.XPATH,
                                       # "//main/div[2]/div[3]/div[3]/ul/li/a"
                                       "./ul[contains(@class, 'odds-tabs')]/li[contains(@class, 'odds-item')]"
                                       )

            for tab in tabs:
                try:
                    if not tab.is_displayed():
                        continue

                    label = tab.text
                    tab.click()
                    # actions.move_to_element(tab).click_and_hold(tab).perform()

                    # Wait for table to load
                    wait.until(
                        EC.presence_of_element_located(
                            # (By.XPATH, "//main/div[2]/div[4]/div/div/div[2]"))
                            (By.XPATH, "//main/div[2]/div[4]"))
                        # (By.XPATH, "//main/div[2]/div[4]/div/div"))
                    )

                    result = self.scrape_data(label, match)
                    if result:
                        data.update(result)

                except (TimeoutException, NoSuchElementException) as e:
                    continue

            print(" >> Checking more tabs.....")
            """""""""""""""""""""
            CHECK FOR MORE TABS
            """""""""""""""""""""
            more_tabs = None
            try:
                # Get hidden "more tab" links
                tab = table.find_element(
                    By.XPATH, "./button[contains(@class, 'toggle-odds')]")
                actions.move_to_element(tab).perform()
                links = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".prio-odds > .hidden-links"))
                )
                more_tabs = links.find_elements(By.TAG_NAME, "li")
            except (TimeoutException, NoSuchElementException) as e:
                print(" >> extract_odds_data() INFO: No more tabs")
                return data, True

            """""""""""""""""""""""""""""""""""
            CHECK IF "MORE TABS" CONTAIN LINKS
            """""""""""""""""""""""""""""""""""
            more_tab_links = []
            while len(more_tab_links) != len(more_tabs) + 1:
                try:
                    wait.until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, ".prio-odds > .hidden-links"))
                    )
                    text = ""
                    for tab in more_tabs:
                        if tab.text not in more_tab_links:
                            text = tab.text
                            tab = wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH,
                                     "//*[contains(text(),\"{}\")]".format(text)))
                            )
                            tab.click()
                            break

                    more_tab_links.append(text)

                    # Wait for table to load
                    wait.until(
                        EC.presence_of_element_located(
                            # (By.XPATH, "//main/div[2]/div[4]"))
                            (By.XPATH, "//main/div[2]/div[4]/div/div"))
                    )
                    result = self.scrape_data(text, match)
                    data.update(result)

                    # Refresh web elements
                    table = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "//div[contains(@class, 'prio-odds')]/div")
                        )
                    )
                    tab = table.find_element(
                        By.XPATH, "./button[contains(@class, 'toggle-odds')]")
                    actions.move_to_element(tab).click_and_hold(tab).perform()
                    links = wait.until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, ".prio-odds > .hidden-links"))
                    )
                    more_tabs = links.find_elements(By.TAG_NAME, "li")

                except (NoSuchElementException, TimeoutException) as e:
                    # No links found under "More Tabs"
                    print(" >> extract_odds_data() INFO: No more tabs")
                    continue

            # Return data after scraping mroe tabs
            return data, True

        except (ElementClickInterceptedException, TimeoutException) as e:
            print("extract_odds_data() error: ", e)
            return {}, False

    def scrape_data(self, tab, match=""):
        try:
            print("   ", tab, "extracting data...")
            time.sleep(1)
            data = dict()
            driver = self.driver
            wait = WebDriverWait(driver, 10)

            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//main/div[2]/div[4]"))
            )

            table = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//main/div[2]/div[4]"))
            )
            content = table.get_attribute("innerHTML")

            if tab in self.table_tabs:
                data = self.scrape_table_layout(tab, content)
            elif tab in self.div_tabs:
                data = self.scrape_div_layout(tab, content)
            elif tab in self.other_tabs:
                data = self.scrape_div_rows(tab, content, match)

            return data
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
            print("scrape_data() error: ", str(e))
            return {}

    def scrape_table_layout(self, tab, content):
        try:
            dom = html.fromstring(content)
            table = dom.xpath("//div/div")[0]
            headers = table.xpath("//div/div/span/p")

            # Some matches contain an incorrect layout for CS
            if not headers:
                return {}

            labels = []
            for header in headers:
                labels.append(header.text)

            row = table.xpath(
                "//div/div/p[contains(text(),'Average')]/../..")[0]

            cells = row.xpath("./div")
            if len(cells) == 0:
                return data

            name = cells[0].xpath('string(.)')
            data_row = {}

            if len(cells) > 1:
                label = self.shorten_label(tab, labels[1])
                data_1 = cells[1].xpath('string(.)')
                data_row.update({label: data_1})

            if len(cells) > 2 and len(labels) > 2:
                label = self.shorten_label(tab, labels[2])
                data_2 = cells[2].xpath('string(.)')
                data_row.update({label: data_2})

            if len(cells) > 3 and len(labels) > 3:
                label = self.shorten_label(tab, labels[3])
                data_3 = cells[3].xpath('string(.)')
                data_row.update({label: data_3})

            if len(cells) > 4 and len(labels) > 4:
                label = self.shorten_label(tab, labels[4])
                data_4 = cells[4].xpath('string(.)')
                data_row.update({label: data_4})

            return data_row

        except (Exception, NoSuchElementException) as e:
            print("scrape_table_layout() error: ", str(e))

    def scrape_div_layout(self, tab, content):
        try:
            dom = html.fromstring(content)
            table = dom.xpath("//div/div")[0]
            headers = table.xpath("//div/div/span/p")

            # Note: Labels are not in order
            # i.e Handicap Payout 2 1
            labels = []
            for header in headers:
                labels.append(header.text)

            rows = table.xpath("//div[position() > 1]")
            data_row = {}
            for row in rows:
                name = row.xpath("string(./div/div[2]/p[1])")
                cells = row.xpath("./div/div[last()]/div")

                if not name.strip() or len(cells) == 0 or len(labels) == 0 or name.strip() == "Handicap":
                    continue

                # Skip 1st cell for label
                if len(cells) > 0 and len(labels) > 1:
                    label = self.shorten_label(name, labels[1])

                    data_1 = cells[0].xpath('string(./div/div/p)')
                    data_row.update({label: data_1})

                if len(cells) > 1 and len(labels) > 2:
                    label = self.shorten_label(name, labels[2])

                    data_2 = cells[1].xpath('string(./div/div/p)')
                    data_row.update({label: data_2})

                if len(cells) > 2 and len(labels) > 3 and "payout" not in labels[3].lower():
                    label = self.shorten_label(name, labels[3])

                    data_3 = cells[2].xpath('string(./div/div/p)')
                    data_row.update({label: data_3})

            return data_row

        except Exception as e:
            print("scrape_div_layout() error: ", e)

    def shorten_label(self, label, index):
        label = label.lower().strip()

        if '1x2' in label:
            label = label.replace('1x2', '')
        elif 'asian handicap' in label:
            label = label.replace('asian handicap', 'AH')
        elif 'over/under' in label:
            label = label.replace('over/under', 'OU')
        elif 'european handicap' in label:
            label = label.replace('european handicap', 'EH')
        elif 'half time / full time' in label:
            label = label.replace('half time / full time', 'HTFT')
            index = index.replace(" / ", '_')
        elif 'correct score' in label:
            label = label.replace('correct score', 'CS')
            index = index.replace(':', '_')
        elif 'draw no bet' in label:
            label = label.replace('draw no bet', 'DNB')
        elif 'both teams to score' in label:
            label = label.replace('both teams to score', 'BTS')
        elif 'odd or even' in label:
            label = label.replace('odd or even', 'OE')
        elif 'double chance' in label:
            label = label.replace('double chance', 'DC')

        if label:
            label = label.replace(' ', '_')
            return "{}-{}".format(label, index.strip())

        return index.strip().upper()

    def scrape_div_rows(self, tab, content, match):
        try:
            dom = html.fromstring(content)
            home_team, away_team = match.split("–")

            rows = dom.xpath("./div")

            data_row = {}
            for row in rows:
                label = row.xpath("string(./div/div[2]/p)")

                # [contains(@class, 'avg')]")
                cells = row.xpath("./div/div[3]")

                if len(cells) == 0:
                    continue

                label = self.shorten_label(tab, label)

                # Shorten label for HTFT
                if tab == "Half Time / Full Time":
                    label = label.replace(home_team.strip(), "HT")
                    label = label.replace(away_team.strip(), "AT")
                    label = label.replace("Draw", "D")

                value = cells[0].xpath('string(./div/div/div/p)')
                data_row.update({
                    label: value
                })

            return data_row

        except Exception as e:
            print("scrape_div_rows() error: ", e)

    def get_pagination(self, url):
        driver = self.driver
        wait = WebDriverWait(driver, 20)

        try:
            driver.get("https://www.oddsportal.com/")
            # Accept Cookies
            button = wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR,
                     "div#onetrust-button-group > button#onetrust-accept-btn-handler")
                )
            )

            button.click()

        except Exception as e:
            pass

        try:
            driver.get(url)

            wait.until(
                EC.visibility_of_element_located(
                    # (By.XPATH, "//main/div[2]/div[5]/div[4]/div/div[@id='pagination']")
                    # (By.XPATH, "//main/div[2]/div[2]/ul/li/a")
                    (By.XPATH,
                     "//main/div[2]/div[5]/div[4]/div/div[@id='pagination']/a")
                )
            )

            pages = driver.find_elements(By.XPATH,
                                         # "//main/div[2]/div[5]/div[4]/div/div[@id='pagination']/a")
                                         "//main/div[2]/div[5]/div[4]/div/div[@id='pagination']/a")

            page_links = {}
            for page in pages:
                num = page.get_attribute("x-page")
                link = page.get_attribute(":href")

                page_links[num] = link

            return page_links

        except (TimeoutException, NoSuchElementException) as e:
            # If scraping future matches, no pagination is found
            print("get_pagination() error: ", e)
            return {"1": url}

    def end(self):
        self.driver.close()
        print("DONE")
