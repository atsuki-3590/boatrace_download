import scrapy


class InfoSpiderSpider(scrapy.Spider):
    name = "info_spider"
    allowed_domains = ["www1.mbrace.or.jp"]
    start_urls = ["http://www1.mbrace.or.jp"]

    def parse(self, response):
        pass
