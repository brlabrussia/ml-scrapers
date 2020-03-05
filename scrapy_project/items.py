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
    """

    # Predefined name of the source which we scrape.
    # Set as `source_name` attribute in every review spider.
    source = scrapy.Field()

    # Name of reviewed bookmaker as it's written on the website.
    bookmaker = scrapy.Field()
    # Rating given by reviewer to reviewed bookmaker.
    rating = scrapy.Field()
    username = scrapy.Field()
    create_dtime = scrapy.Field()

    # `title`, `comment`, `pluses` and `minuses` fields are only needed to build nicely
    # formatted `content` field (if possible it's to parse them) with BuildContentPipeline.
    # Otherwise scrape from page straight into `content` field.
    content = scrapy.Field()
    title = scrapy.Field()
    pluses = scrapy.Field()
    minuses = scrapy.Field()
    comment = scrapy.Field()


class ReviewLoader(ItemLoader):
    """
    Item Loader for `Review` item which is the main item for any review site.
    """

    default_item_class = Review
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    rating_in = MapCompose(float)
    create_dtime_in = MapCompose(format_date)

    content_out = Join("")
