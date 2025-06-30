# settings.py

BOT_NAME = 'odds_scrapy'
SPIDER_MODULES = ['odds_scrapy.spiders']
NEWSPIDER_MODULE = 'odds_scrapy.spiders'

# 適切なUSER_AGENTを設定
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Robots.txtを遵守
ROBOTSTXT_OBEY = True

# 自動スロットル調整
AUTOTHROTTLE_ENABLED = True
# 最初のダウンロード遅延（秒）
AUTOTHROTTLE_START_DELAY = 5
# 負荷が高い場合に到達しうる最大ダウンロード遅延（秒）
AUTOTHROTTLE_MAX_DELAY = 60
# 並列リクエスト数の平均値
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 同時リクエスト数を設定
CONCURRENT_REQUESTS = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# HTTPキャッシュを有効にする（開発中に非常に便利）
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0 # 0にするとキャッシュが期限切れにならない
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'