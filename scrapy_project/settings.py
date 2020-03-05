BOT_NAME = "scrapy_project"

SPIDER_MODULES = ["scrapy_project.spiders"]
NEWSPIDER_MODULE = "scrapy_project.spiders"

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    "scrapy_project.pipelines.NormalizeValuesPipeline": 1,
    "scrapy_project.pipelines.NormalizeDatePipeline": 2,
    "scrapy_project.pipelines.BuildContentPipeline": 3,
}

FEED_EXPORT_ENCODING = "utf-8"
