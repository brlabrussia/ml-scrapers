import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join


# Same as scrapy.loader.processors.TakeFirst, but blanks are acceptable
def default_output_processor(self, values):
    for value in values:
        if value is not None and value != "":
            return value
    else:
        return ""


# Same as in ratings_parser.models, might change later
class Bookmaker(scrapy.Item):
    external_id = scrapy.Field()
    external_name = scrapy.Field()


# Same as dict returned in collector.parsers.reviews_parsers, might change later
class Review(scrapy.Item):
    bookmaker = scrapy.Field()
    source = scrapy.Field()

    content = scrapy.Field()
    title = scrapy.Field()
    comment = scrapy.Field()
    pluses = scrapy.Field()
    minuses = scrapy.Field()

    rating = scrapy.Field()
    username = scrapy.Field()
    create_dtime = scrapy.Field()


class ReviewLoader(ItemLoader):
    default_item_class = Review
    default_output_processor = default_output_processor

    content_in = Join("")
