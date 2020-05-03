import fake_useragent

BOT_NAME = 'sentiment_ru'

SPIDER_MODULES = ['sentiment_ru.spiders']
NEWSPIDER_MODULE = 'sentiment_ru.spiders'

USER_AGENT = fake_useragent.UserAgent().chrome

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

TELNETCONSOLE_ENABLED = False

SPIDER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES = {}

ITEM_PIPELINES = {
    'sentiment_ru.pipelines.BuildContentPipeline': 1,
    'sentiment_ru.pipelines.WebhookPipeline': 800,
}

FEED_EXPORT_ENCODING = 'utf-8'

LOG_LEVEL = 'INFO'

# Proxy settings https://github.com/TeamHG-Memex/scrapy-rotating-proxies
ROTATING_PROXY_LIST_PATH = 'proxies.txt'
DOWNLOADER_MIDDLEWARES.update({
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
})

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
