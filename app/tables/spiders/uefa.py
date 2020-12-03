import scrapy

from default.utils import StartUrlsMixin
from tables.items import TableDataLoader, TableLoader


class UefaSpider(StartUrlsMixin, scrapy.Spider):
    name = 'uefa'
    allowed_domains = ['uefa.com']
    start_urls = ['https://ru.uefa.com/memberassociations/uefarankings/country/#/yr/2020']

    def start_requests(self):
        url = self.start_urls[0]
        if '#/yr/' in url:
            url = url.replace('#/yr/', 'libraries/years/')
        yield scrapy.Request(url)

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        table_sel = response.css('.table--standings')

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
        for row_sel in table_sel.css('tbody tr'):
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
