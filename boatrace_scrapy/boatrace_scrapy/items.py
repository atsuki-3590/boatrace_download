# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class InfoItem(scrapy.Item):
    # レースの基本情報
    race_code = scrapy.Field()
    title = scrapy.Field()
    day_num = scrapy.Field()
    date = scrapy.Field()
    stadium = scrapy.Field()
    race_round = scrapy.Field()
    race_name = scrapy.Field()
    distance = scrapy.Field()
    post_time = scrapy.Field()

    # 選手ごとの情報を格納するためのフィールド
    # 辞書のリストとして格納することを想定 [ {player1_data}, {player2_data}, ... ]
    players_data = scrapy.Field()

class OddsScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
