from default.settings import *

BOT_NAME = 'sentiment_ru'

SPIDER_MODULES = ['sentiment_ru.spiders']
NEWSPIDER_MODULE = 'sentiment_ru.spiders'

CONCURRENT_REQUESTS = 16

ITEM_PIPELINES.update({
    'sentiment_ru.pipelines.BuildContentPipeline': 1,
})
