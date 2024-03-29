import re

import scrapy
from scrapy.loader.processors import Compose

from default.utils import StartUrlsMixin
from tables.items_ import TableDataLoader, TableLoader
from tables.utils import BASIC_POST_PROCESSOR, prepare_table_selector


class CybersportSpider(StartUrlsMixin, scrapy.Spider):
    name = 'cybersport'
    allowed_domains = ['cybersport.ru']
    start_urls = ['https://www.cybersport.ru/base/gamers?page=1&disciplines=21']

    post_processor = Compose(
        BASIC_POST_PROCESSOR,
        lambda x: x.replace('image:url(/', 'image:url(https://www.cybersport.ru/'),
        lambda x: x.replace('image:url(../', 'image:url(https://www.cybersport.ru/assets/'),
        lambda x: re.sub(r'(<i[^>]*?/assets/flags/.*?>)', r'\1<br>', x, flags=re.S),
    )

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', 'article h1::text')
        table_sel = response.css('article table')
        table_sel = prepare_table_selector(
            table_sel,
            response,
            styletags=False,
            post_processor=self.post_processor,
        )

        # head
        for row_sel in table_sel.css('thead tr'):
            row_loaders = []
            for data_sel in row_sel.css('th'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('style', './@style')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.css('tbody tr'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('style', './@style')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
