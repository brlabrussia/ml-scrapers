from default.settings import *

BOT_NAME = 'tables'
SPIDER_MODULES = ['tables.spiders']
NEWSPIDER_MODULE = 'tables.spiders'

ITEM_PIPELINES = {
    'tables.pipelines.WebhookPipeline': 800,
}
