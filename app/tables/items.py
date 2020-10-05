import re

import bleach
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, MapCompose, TakeFirst, Compose

ALLOWED_TAGS = [
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'br',
    'code',
    'em',
    'i',
    'img',
    'strong',
    'sub',
    'sup',
]

ALLOWED_ATTRIBUTES = {
    'img': [
        'alt',
        'height',
        'src',
        'width',
    ],
}


def normalize_tags(text: str) -> str:
    text = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
    return text


def normalize_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


class Table(Item):
    url = Field()
    title = Field()
    head = Field()
    body = Field()
    foot = Field()


class TableData(Item):
    value = Field()
    colspan = Field()
    rowspan = Field()
    text_align = Field()


class TableLoader(ItemLoader):
    default_item_class = Table
    title_in = MapCompose(normalize_spaces)
    default_output_processor = TakeFirst()

    head_out = body_out = foot_out = MapCompose(
        lambda table_row: [[dict(il.load_item()) for il in table_row]],
    )


class TableDataLoader(ItemLoader):
    default_item_class = TableData
    default_output_processor = Compose(Join(), normalize_spaces)

    value_out = Compose(Join(), normalize_tags, normalize_spaces)
