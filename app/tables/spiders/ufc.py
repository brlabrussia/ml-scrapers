import re

import scrapy
from scrapy.loader.processors import Compose

from tables.items_ import TableDataLoader, TableLoader
from tables.utils import (
    normalize_style_attributes,
    prepare_table_selector,
    remove_browser_css_properties,
    remove_color_css_properties,
    remove_style_tags,
    remove_weird_css_properties,
    replace_anchors,
)


class UfcSpider(scrapy.Spider):
    name = 'ufc'
    allowed_domains = ['bsrussia.com']
    start_urls = ['https://ru.ufc.com/rankings']
    table_name = 'Полусредний вес'
    post_processor = Compose(
        remove_style_tags,
        # remove_unwanted_attributes,
        normalize_style_attributes,
        remove_browser_css_properties,
        # remove_weird_css_properties,
        remove_color_css_properties,
        replace_anchors,
        lambda x: x.replace('visibility:hidden;', ''),
        lambda x: re.sub(r'border-bottom.*?;', r'', x, flags=re.S),
        # lambda x: re.sub(r'\s(class|href)="[^"]*?"', r'', x, flags=re.S),
    )

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.table_name)
        xp = f'//*[@class="info"]/h4[normalize-space(text())="{self.table_name}"]/ancestor::table'
        table_sel = prepare_table_selector(
            response.css('body'),
            response,
            post_processor=self.post_processor,
        )
        table_sel = table_sel.xpath(xp)

        # upper body
        row_loaders = []
        tdl = TableDataLoader(selector=table_sel)
        tdl.add_xpath('value', './/caption/node()')
        tdl.add_value('value', '')
        tdl.add_value('colspan', '3')
        row_loaders.append(tdl)
        tl.add_value('body', [row_loaders])

        # rest of body
        for row_sel in table_sel.css('tbody tr'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
