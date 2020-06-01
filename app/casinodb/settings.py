from default.settings import *

BOT_NAME = 'casinodb'
SPIDER_MODULES = ['casinodb.spiders']
NEWSPIDER_MODULE = 'casinodb.spiders'

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_EXPIRATION_SECS = 3600 * 36  # 36 hours
HTTPCACHE_POLICY = 'casinodb.extensions.CasinoguruCachePolicy'
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

CASINOGURU_CUSTOM_SETTINGS = {
    'NORDVPN_ENABLED': True,
    'CONCURRENT_REQUESTS': 1,
    'DOWNLOAD_DELAY': 0.5,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 5,
    'AUTOTHROTTLE_MAX_DELAY': 60,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
}
