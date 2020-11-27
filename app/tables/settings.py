from default.settings import *

BOT_NAME = 'tables'
SPIDER_MODULES = ['tables.spiders']
NEWSPIDER_MODULE = 'tables.spiders'

ITEM_PIPELINES = {
    'tables.pipelines.WebhookPipeline': 800,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_EXPIRATION_SECS = 3600 * 4
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
