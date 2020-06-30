from default.settings import *

BOT_NAME = 'sentiment_ratings'

SPIDER_MODULES = ['sentiment_ratings.spiders']
NEWSPIDER_MODULE = 'sentiment_ratings.spiders'

CONCURRENT_REQUESTS = 16

ITEM_PIPELINES.update({
    'default.pipelines.ScrapyMetaFieldPipeline': 1,
    'default.pipelines.SentimentSourceFieldPipeline': 2,
})
