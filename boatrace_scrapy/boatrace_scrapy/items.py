# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# InfoItemはそのまま
class InfoItem(scrapy.Item):
    race_code = scrapy.Field()
    title = scrapy.Field()
    day_num = scrapy.Field()
    date = scrapy.Field()
    stadium = scrapy.Field()
    race_round = scrapy.Field()
    race_name = scrapy.Field()
    distance = scrapy.Field()
    post_time = scrapy.Field()
    players_data = scrapy.Field()

# ResultItemを追加
class ResultItem(scrapy.Item):
    race_code = scrapy.Field()
    title = scrapy.Field()
    day = scrapy.Field()
    date = scrapy.Field()
    stadium = scrapy.Field()
    race_round = scrapy.Field()
    race_name = scrapy.Field()
    distance = scrapy.Field()
    weather = scrapy.Field()
    wind_direction = scrapy.Field()
    wind_velocity = scrapy.Field()
    wave_height = scrapy.Field()
    winning_technique = scrapy.Field()
    result_win = scrapy.Field()
    result_place_show = scrapy.Field()
    result_exacta = scrapy.Field()
    result_quinella = scrapy.Field()
    result_quinella_place = scrapy.Field()
    result_trifecta = scrapy.Field()
    result_trio = scrapy.Field()
    result_racer = scrapy.Field()  # 1～6艇分の選手データをカンマ区切りで格納

class OddsScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
