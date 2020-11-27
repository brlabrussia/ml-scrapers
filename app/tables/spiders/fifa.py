import re

from scrapy.loader.processors import Compose

from tables.items_ import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider
from tables.utils import BASIC_POST_PROCESSOR, prepare_table_selector


class FifaSpider(DefaultSpider):
    name = 'fifa'
    allowed_domains = ['fifa.com']
    start_urls = ['https://www.fifa.com/fifa-world-ranking/ranking-table/men/']
    post_processor = Compose(
        BASIC_POST_PROCESSOR,
        lambda x: re.sub(r'<abbr.*?</abbr>', r'', x, flags=re.S),
        lambda x: re.sub(r'border[^;"]+?;\s?', r'', x, flags=re.S),
    )

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.fi-ranking-schedule__title::text')
        tl.add_xpath('extra', '//svg[has-class("fi-module-ranking__ranking__item__arrow")]/defs/..')
        table_sel = response.css('#rank-table')
        table_sel = prepare_table_selector(
            table_sel,
            response,
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
                if (
                    hasattr(self, 'args')
                    and len(self.args) != 0
                    and 'display:none;' in data_sel.css('::attr(style)').get()
                    and f'#{self.args[0]}#' != data_sel.css('span::text').get()
                ):
                    break
            else:
                tl.add_value('body', [row_loaders])

        yield tl.load_item()
