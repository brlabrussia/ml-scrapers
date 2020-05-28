from glob import glob
from http import HTTPStatus

from fake_useragent import UserAgent

BOT_NAME = 'default'

SPIDER_MODULES = [path.replace('/', '.') for path in glob('*/spiders')]
NEWSPIDER_MODULE = None

ROBOTSTXT_OBEY = False
COOKIES_ENABLED = True
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
USER_AGENT = UserAgent(cache=False, fallback=USER_AGENT).chrome

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 0
AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [hs.value for hs in HTTPStatus if hs.value != 200]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

LOG_LEVEL = 'INFO'
FEED_EXPORT_ENCODING = 'utf-8'
TELNETCONSOLE_ENABLED = False
IMAGES_STORE = '.scrapy/images'

SPIDER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES = {
   'default.middlewares.NordVPNProxyMiddleware': 350,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
}

ITEM_PIPELINES = {
   'default.pipelines.WebhookPipeline': 800,
}

# Splash settings https://github.com/scrapy-plugins/scrapy-splash
SPLASH_URL = 'http://splash:8050/'
DOWNLOADER_MIDDLEWARES.update({
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
})
SPIDER_MIDDLEWARES.update({
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
})
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
