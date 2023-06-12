import argparse
import time
import pandas as pd

from oddsportal import OddsPortalScraper


def get_column_order(matches):
    column_template = [
        "Match",
        "Date",
        "Home Team",
        "Away Team",
        "Home Team Goals",
        "Away Team Goals",
        "1",
        "X",
        "2",
        "-AH",
        "-OU",
        "-DNB",
        "-EH",
        "-DC",
        "-CS",
        "-HTFT",
        "-OE",
        "-BTS"
    ]

    expanded_keys = {
        "AH": [],
        "OU": [],
        "DNB": [],
        "EH": [],
        "DC": [],
        "CS": [],
        "HTFT": [],
        "OE": [],
        "BTS": []
    }

    for _, match in matches.items():
        for k in match.keys():
            if "_" not in k and '-' not in k:
                continue

            id = k.split("_")[0].split("-")[0]
            if id not in expanded_keys:
                continue

            expanded_keys[id].append(k)

    ordered_columns = []
    for c in column_template:
        if '-' not in c:
            ordered_columns.append(c)
            continue

        ordered_columns.extend(sorted(set(expanded_keys[c[1:]])))

    return ordered_columns


def format_data(country, league, season, matches):
    if not season:
        season = "current"

    filename = "{}-{}-{}.csv".format(country,
                                     league.replace(" ", "_"), season.replace("/", "_"))

    ordered_columns = get_column_order(matches)
    df = pd.DataFrame.from_dict(matches.values())
    df.to_csv(filename, columns=ordered_columns, index=False)


def do_scrape(scraper, url, first_n_matches):
    all_match = {}

    pages = scraper.get_pagination(url)

    if '2' in pages:
       pages = {
           '1': pages['2'].replace('page/2', 'page/1'),
           **pages
       }

    for id, page_link in pages.items():
        print("======= PAGE LINK: ", page_link)
        matches = scraper.get_matches(page_link, url)

        num_matches = 1
        for match, link in matches.items():
            # Skip blank name
            if not match.strip():
                continue

            print("Scraping match: ", match, "--", link)

            if link not in all_match:
                all_match[link] = {}

            results, is_ok = scraper.extract_odds_data(link, match, )

            retry = 0
            while not is_ok and retry < 3:
                print("  > Retrying ", match)
                results, is_ok = scraper.extract_odds_data(link, match)

                retry += 1
                time.sleep(1)

            all_match[link] = results

            # For test purposes only
            if num_matches == first_n_matches:
                break

            num_matches += 1

    return all_match


def run(args):
    country = args.country
    league = args.league
    season = args.season
    linux = args.linux
    num_match = args.num_match

    # Build URL based on arguments
    url = "https://www.oddsportal.com/soccer/{}/{}".format(
        country, league.replace(" ", "-"))

    if season:
        url = "{}-{}/results/".format(url, season.replace("/", "-"))

    driver = "chromedriver" if linux else "chromedriver.exe"
    scraper = OddsPortalScraper(driver)

    # Where the magic happens
    matches = do_scrape(scraper, url, num_match)

    format_data(country, league, season, matches)

    scraper.end()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Odds Portal Website")
    parser.add_argument(
        "--country", help="Country to select the leagues (i.e england)", required=True)
    parser.add_argument(
        "--league", help="League in the country (i.e premier league)", required=True)
    parser.add_argument(
        "--season", help="Season to scrape (i.e 2021/2022)", default="")
    parser.add_argument(
        "--linux", action="store_true")
    parser.add_argument(
        "--num_match", help="Scrape only N matches", default=9999999, type=int)

    args = parser.parse_args()

    run(args)
