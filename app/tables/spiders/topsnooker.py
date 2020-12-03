import scrapy

from default.utils import StartUrlsMixin
from tables.items import TableDataLoader, TableLoader


class TopsnookerSpider(StartUrlsMixin, scrapy.Spider):
    name = 'topsnooker'
    allowed_domains = ['topsnooker.com']
    start_urls = ['http://top-snooker.com/world-rankings/']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.pix-page-title::text')
        table_sel = response.css('.pix-content-wrap table')

        # head
        for row_sel in table_sel.css('thead tr'):
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
        for row_i, row_sel in enumerate(table_sel.css('tbody tr')):
            row_loaders = []
            for data_i, data_sel in enumerate(row_sel.css('td')):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                if data_i == 0:
                    tdl.add_value('value', str(row_i + 1))
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
