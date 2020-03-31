BOT_NAME = "sentiment_ru"

SPIDER_MODULES = ["sentiment_ru.spiders"]
NEWSPIDER_MODULE = "sentiment_ru.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16

TELNETCONSOLE_ENABLED = False

ITEM_PIPELINES = {
    "sentiment_ru.pipelines.BuildContentPipeline": 1,
    "sentiment_ru.pipelines.PostgresPipeline": 200,
}

# FEED_URI = "export"
# FEED_FORMAT = "jsonlines"
# FEED_EXPORT_ENCODING = "utf-8"

LOG_LEVEL = "INFO"
