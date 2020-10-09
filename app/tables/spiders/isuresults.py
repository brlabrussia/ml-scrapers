from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class IsuresultsSpider(DefaultSpider):
    name = 'isuresults'
    allowed_domains = ['isuresults.com']
    start_urls = ['http://www.isuresults.com/ws/ws/wsmen.htm']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', 'tr td.flx1::text')
        table_sel = response.css('table')

        # head
        for row_sel in table_sel.css('tr')[5:7]:
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.css('tr')[7:-4]:
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
