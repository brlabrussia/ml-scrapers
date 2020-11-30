from default.settings import *

BOT_NAME = 'casino'
SPIDER_MODULES = ['casino.spiders']
NEWSPIDER_MODULE = 'casino.spiders'

NORDVPN_ENABLED = True

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_EXPIRATION_SECS = 3600 * 36  # 36 hours
HTTPCACHE_POLICY = 'casino.extensions.CasinoguruCachePolicy'
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

CASINOGURU_CUSTOM_SETTINGS = {
    'CONCURRENT_REQUESTS': 1,
    'DOWNLOAD_DELAY': 0.5,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 5,
    'AUTOTHROTTLE_MAX_DELAY': 60,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
}
