# settings.py

BOT_NAME = 'odds_scrapy'
SPIDER_MODULES = ['odds_scrapy.spiders']
NEWSPIDER_MODULE = 'odds_scrapy.spiders'

# 適切なUSER_AGENTを設定
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# 適度なダウンロードディレイを設定
DOWNLOAD_DELAY = 1

# 同時リクエスト数を設定
CONCURRENT_REQUESTS = 20

# Robots.txtの遵守を無効化
ROBOTSTXT_OBEY = False