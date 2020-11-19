import re
from urllib.parse import urljoin

import bleach
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

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
    width = Field()
    height = Field()
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

    @property
    def value_out(self):
        return Compose(
            Join(),
            normalize_tags,
            normalize_spaces,
            self.rel_to_abs,
            lambda x: x.replace('&amp;', '&'),
        )

    def rel_to_abs(self, text: str) -> str:
        if not hasattr(self, 'base_url') or 'src' not in text:
            return text
        for src in re.findall('src="([^"]*)"', text):
            if src.startswith('http'):
                continue
            text = text.replace(src, urljoin(self.base_url, src))
        return text
