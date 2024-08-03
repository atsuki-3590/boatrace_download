import scrapy


class OddsSpiderSpider(scrapy.Spider):
    name = "odds_spider"
    allowed_domains = ["boatrace.jp"]
    start_urls = ["https://boatrace.jp"]

    def parse(self, response):
        pass
