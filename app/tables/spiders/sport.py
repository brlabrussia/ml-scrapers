import scrapy

from tables.items import TableDataLoader, TableLoader


class SportSpider(scrapy.Spider):
    name = 'sport'
    allowed_domains = ['sport.ru', 'google.com']
    start_urls = ['https://www.sport.ru/tennis/wta/rating-gonka/']

    def parse(self, response):
        link = response.css('.tag-page-content iframe::attr(src)').get()
        link = link.replace('/pubhtml', '/pubhtml/sheet')
        yield response.follow(link, self.parse_)

    def parse_(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        table_sel = response.css('table')

        # head
        for index, row_sel in enumerate(table_sel.css('tr')):
            if 'Место' not in row_sel.get():
                continue
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
            break

        # body
        for row_sel in table_sel.css('tr')[index+1:]:
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
