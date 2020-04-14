import dateparser
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def format_date(date):
    """
    Take any scraped date and format it to ISO, return `None` on failure.
    """
    settings = {"TIMEZONE": "Europe/Moscow", "RETURN_AS_TIMEZONE_AWARE": True}
    date = dateparser.parse(date, settings=settings)
    if date is None:
        return None
    date = date.isoformat()
    return date


class Review(scrapy.Item):
    """
    Main item for any review site.

    `content_title`, `content_positive`, `content_negative` and `content_comment` fields are only needed
    to build nicely formatted `content` field (if it's possible to parse them) with BuildContentPipeline.
    Otherwise scrape from page straight into `content` field.
    """

    author = scrapy.Field()
    content = scrapy.Field()
    content_title = scrapy.Field()
    content_positive = scrapy.Field()
    content_negative = scrapy.Field()
    content_comment = scrapy.Field()
    rating = scrapy.Field()
    rating_max = scrapy.Field()
    rating_min = scrapy.Field()
    subject = scrapy.Field()
    time = scrapy.Field()
    type = scrapy.Field()
    url = scrapy.Field()


class ReviewLoader(ItemLoader):
    """
    Item Loader for `Review` item which is the main item for any review site.
    """

    default_item_class = Review
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    content_out = Join("")
    rating_in = MapCompose(float)
    rating_max_in = MapCompose(float)
    rating_min_in = MapCompose(float)
    time_in = MapCompose(format_date)
