import scrapy

from tables.items import TableDataLoader, TableLoader


class FibaSpider(scrapy.Spider):
    name = 'fiba'
    allowed_domains = ['fiba.basketball']
    start_urls = ['https://www.fiba.basketball/rankingmen']

    def start_requests(self):
        url = self.start_urls[0]
        if 'https://' in url:
            url = url.replace('https://', 'https://webcache.googleusercontent.com/search?q=cache:')
        yield scrapy.Request(url)

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', 'li#fiba h5::text')
        table_sel = response.css('li#fiba .fiba_ranking_table')

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
