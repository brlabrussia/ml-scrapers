BOT_NAME = "scrapy_project"

SPIDER_MODULES = ["scrapy_project.spiders"]
NEWSPIDER_MODULE = "scrapy_project.spiders"

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    "scrapy_project.pipelines.BuildContentPipeline": 1,
}

FEED_EXPORT_ENCODING = "utf-8"
