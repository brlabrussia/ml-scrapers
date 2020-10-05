from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class FivbSpider(DefaultSpider):
    name = 'fivb'
    allowed_domains = ['fivb.com', 'hypercube.nl']
    start_urls = ['https://www.fivb.com/en/volleyball/rankings/seniorworldrankingmen']

    def parse(self, response):
        url = response.css('.content-box iframe::attr(src)').get()
        yield response.follow(url, self.parse_)

    def parse_(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', self.start_urls[0])
        tl.add_css('title', '.title-holder h3::text')
        table_sel = response.css('table')

        # head
        for row_sel in table_sel.css('thead tr'):
            row_loaders = []
            for data_sel in row_sel.css('th'):
                tdl = TableDataLoader(selector=data_sel)
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
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
