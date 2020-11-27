from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

from default.items import normalize_space


class Table(Item):
    url = Field()
    title = Field()
    extra = Field()
    head = Field()
    body = Field()
    foot = Field()


class TableData(Item):
    value = Field()
    style = Field()
    colspan = Field()
    rowspan = Field()
    width = Field()
    height = Field()
    text_align = Field()


class TableLoader(ItemLoader):
    default_item_class = Table
    title_in = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    head_out = body_out = foot_out = MapCompose(
        lambda table_row: [[dict(il.load_item()) for il in table_row]],
    )


class TableDataLoader(ItemLoader):
    default_item_class = TableData
    default_output_processor = Compose(Join(), normalize_space)

    value_out = Compose(
        Join(),
        normalize_space,
        lambda x: x.replace('&amp;', '&'),
        normalize_space,
    )
