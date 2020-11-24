import re
from typing import Optional

import dateparser
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


def normalize_space(string: str) -> str:
    """
    Replaces sequences of whitespace characters by a single space,
    strips leading and trailing white-space from a string,
    and returns the resulting string.
    """
    return re.sub(r'\s+', ' ', string).strip()


def drop_blank(string: str) -> Optional[str]:
    return string if string else None


def format_date(date: str) -> Optional[str]:
    """
    Format date string to ISO, return `None` on failure.
    """
    settings = {'TIMEZONE': 'Europe/Moscow', 'RETURN_AS_TIMEZONE_AWARE': True}
    date = dateparser.parse(normalize_space(date), settings=settings)
    return None if date is None else date.isoformat()


class DefaultLoader(ItemLoader):
    default_input_processor = MapCompose(
        normalize_space,
        drop_blank,
    )
    default_output_processor = TakeFirst()
