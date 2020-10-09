from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class ChampionatSpider(DefaultSpider):
    name = 'championat'
    allowed_domains = ['championat.com']
    start_urls = ['https://www.championat.com/tennis/rating/1/2020/0/']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.entity-header__title-name::text')
        table_sel = response.css('.page-main table:first-of-type')

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
