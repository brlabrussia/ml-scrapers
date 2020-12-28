import re

import bleach
import scrapy
from scrapy.loader.processors import Compose

from default.utils import StartUrlsMixin
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


class UfcSpider(StartUrlsMixin, scrapy.Spider):
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
        # remove_color_css_properties,
        # replace_anchors,
        lambda x: x.replace('visibility:hidden;', ''),
        # lambda x: re.sub(r'border-bottom.*?;', r'', x, flags=re.S),
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
        is_top_rank_table = False
        row_loaders = []
        tdl = TableDataLoader(selector=table_sel)
        value = (
            table_sel.xpath('.//*[@class="info"]/h6/node()').get()
            or table_sel.xpath('.//*[@class="info"]/h4/span/node()').get()
        )
        value = bleach.clean(value, tags=[], strip=True).strip()
        value = f'<b>{value}</b>'
        if 'top rank' in value.lower():
            value = '1'
            is_top_rank_table = True
        if 'чемпион' in value.lower():
            value = '<b>Ч</b>'
        tdl.add_value('value', value)
        row_loaders.append(tdl)

        tdl = TableDataLoader(selector=table_sel)
        value = table_sel.xpath('.//*[has-class("views-row")]').get()
        value = bleach.clean(value, tags=[], strip=True).strip()
        if not is_top_rank_table:
            value = f'<b>{value}</b>'
        if 'khabib nurmagomedov' in value.lower():
            value = 'Хабиб Нурмагомедов'
        elif 'amanda nunes' in value.lower():
            value = 'Аманда Нунис'
        elif 'conor mcgregor' in value.lower():
            value = 'Конор Макгрегор'
        tdl.add_value('value', value)
        row_loaders.append(tdl)

        tdl = TableDataLoader(selector=table_sel)
        tdl.base_url = response.url
        tdl.add_value('value', '')
        row_loaders.append(tdl)

        tl.add_value('body', [row_loaders])

        # rest of body
        for row_sel in table_sel.css('tbody tr'):
            row_loaders = []
            for index, data_sel in enumerate(row_sel.css('td')):
                tdl = TableDataLoader(selector=data_sel)
                value = data_sel.xpath('./node()').get()
                if index in (0, 1):
                    value = bleach.clean(value, tags=[], strip=True)
                tdl.add_value('value', value)
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
