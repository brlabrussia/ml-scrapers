import scrapy

from default.utils import StartUrlsMixin
from tables.items import TableDataLoader, TableLoader


class BsrussiaSpider(StartUrlsMixin, scrapy.Spider):
    name = 'bsrussia'
    allowed_domains = ['bsrussia.com']
    start_urls = ['https://bsrussia.com/ratings/mirovoy-reyting']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.table-wrapper__title::text')
        table_sel = response.css('.table--world-rating')

        # head
        for row_sel in table_sel.css('tr.table__head'):
            row_loaders = []
            for data_sel in row_sel.css('th'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.css('tr.table__row'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
