import scrapy
from scrapy import Request
import cloudscraper


class PlacesSpider(scrapy.Spider):
    name = "places"
    start_urls = []

    def parse(self):
        scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0', })
        url = 'https://www.thuisbezorgd.nl/bestellen/eten/amsterdam-1016'
        req = scraper.get(url)
        print(req)

