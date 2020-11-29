import scrapy

from tables.items import TableDataLoader, TableLoader


class FideSpider(scrapy.Spider):
    name = 'fide'
    allowed_domains = ['fide.com']
    start_urls = ['https://ratings.fide.com/top_lists.phtml?list=women']

    def start_requests(self):
        url = self.start_urls[0]
        if 'top_lists.phtml' in url:
            url = url.replace('top_lists.phtml', 'a_top.php')
        yield scrapy.Request(url)

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.title-page::text')
        table_sel = response.css('table')

        # head
        for row_sel in table_sel.css('thead tr'):
            row_loaders = []
            for data_sel in row_sel.css('th'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.xpath('./tr'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
