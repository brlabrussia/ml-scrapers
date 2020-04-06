from fake_useragent import UserAgent

BOT_NAME = "sentiment_ru"

SPIDER_MODULES = ["sentiment_ru.spiders"]
NEWSPIDER_MODULE = "sentiment_ru.spiders"

USER_AGENT = UserAgent().chrome

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

TELNETCONSOLE_ENABLED = False

SPIDER_MIDDLEWARES = {
    "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
}

ITEM_PIPELINES = {
    "sentiment_ru.pipelines.BuildContentPipeline": 1,
    "sentiment_ru.pipelines.WebhookPipeline": 800,
}

FEED_EXPORT_ENCODING = "utf-8"

LOG_LEVEL = "INFO"

# Splash-related settings
SPLASH_URL = "http://splash:8050/"
DUPEFILTER_CLASS = "scrapy_splash.SplashAwareDupeFilter"
HTTPCACHE_STORAGE = "scrapy_splash.SplashAwareFSCacheStorage"

# Custom settings for WebhookPipeline
WEBHOOK_URLS = ["https://httpbin.org/post"]
WEBHOOK_CHUNK_SIZE = 1000
