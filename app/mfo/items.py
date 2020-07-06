import scrapy
from scrapy.loader.processors import TakeFirst


class VsezaimyonlineItem(scrapy.Item):
    subject = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    ogrn = scrapy.Field(output_processor=TakeFirst())
    inn = scrapy.Field(output_processor=TakeFirst())
    refusal_reasons = scrapy.Field()
    social_networks = scrapy.Field()
    documents = scrapy.Field()
