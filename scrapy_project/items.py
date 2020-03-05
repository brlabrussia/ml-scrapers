import dateparser
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def format_date(date):
    settings = {"TIMEZONE": "Europe/Moscow", "RETURN_AS_TIMEZONE_AWARE": True}
    date = dateparser.parse(date, settings=settings)
    if date is None:
        return None
    date = date.isoformat()
    return date


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
    default_output_processor = TakeFirst()

    bookmaker_in = MapCompose(str.strip)

    content_in = MapCompose(str.strip)
    content_out = Join("")
    title_in = MapCompose(str.strip)
    comment_in = MapCompose(str.strip)
    pluses_in = MapCompose(str.strip)
    minuses_in = MapCompose(str.strip)

    rating_in = MapCompose(float)
    create_dtime_in = MapCompose(format_date)
