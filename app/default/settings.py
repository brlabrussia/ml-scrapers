import os

BOT_NAME = 'default'
SPIDER_MODULES = None
NEWSPIDER_MODULE = None

DEBUG = os.getenv('DEBUG', 0)

if DEBUG:
    LOG_LEVEL = 'DEBUG'
else:
    LOG_LEVEL = 'INFO'

FEED_EXPORT_ENCODING = 'utf-8'
TELNETCONSOLE_ENABLED = False

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'

CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 0
DOWNLOAD_TIMEOUT = 30
DOWNLOAD_MAXSIZE = 20971520  # 20MB

# NordVPNProxyMiddleware
NORDVPN_ENABLED = False
NORDVPN_USERNAME = os.getenv('NORDVPN_USERNAME')
NORDVPN_PASSWORD = os.getenv('NORDVPN_PASSWORD')

# WebhookPipeline
# Currently configured via spider attributes
WEBHOOK_ENABLED = True
WEBHOOK_ENDPOINT = None
WEBHOOK_CHUNK_SIZE = 1000
WEBHOOK_COMPAT = False

# ImagesPipeline
# Project uses custom version which is based on built-in one
# https://docs.scrapy.org/en/latest/topics/media-pipeline.html#scrapy.pipelines.images.ImagesPipeline
IMAGES_ENABLED = False
IMAGES_STORE = '.scrapy/images'
IMAGES_EXPIRES = 3

SPIDER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES = {
    'default.middlewares.NordVPNProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
}

ITEM_PIPELINES = {
    'default.pipelines.ImagesPipeline': 1,
    'default.pipelines.WebhookPipeline': 800,
}

EXTENSIONS = {}

# Splash settings https://github.com/scrapy-plugins/scrapy-splash
SPLASH_URL = os.getenv('SPLASH_URL')
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
SPLASH_LOG_400 = False

if DEBUG:
    HTTPCACHE_ENABLED = True
    HTTPCACHE_DIR = 'httpcache'
    HTTPCACHE_EXPIRATION_SECS = 3600 * 10
    HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
