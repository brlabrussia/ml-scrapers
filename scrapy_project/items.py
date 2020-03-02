import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


# Same as in ratings_parser.models, might change later
class Bookmaker(scrapy.Item):
    external_id = scrapy.Field()
    name = scrapy.Field()


# Same as dict returned in collector.parsers.reviews_parsers, might change later
class Review(scrapy.Item):
    comment = scrapy.Field()
    content = scrapy.Field()
    create_dtime = scrapy.Field()
    minuses = scrapy.Field()
    pluses = scrapy.Field()
    rating = scrapy.Field()
    title = scrapy.Field()
    username = scrapy.Field()


class ReviewLoader(ItemLoader):
    default_item_class = Review
    default_output_processor = TakeFirst()
