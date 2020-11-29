import scrapy

from tables.items import TableDataLoader, TableLoader


class UfcSpider(scrapy.Spider):
    name = 'ufc'
    allowed_domains = ['bsrussia.com']
    start_urls = ['https://ru.ufc.com/rankings']
    table_name = 'Полусредний вес'

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.table_name)
        # xp = f'//*[@class="view-grouping-header"][normalize-space(text())="{self.table_name}"]/following-sibling::*[@class="view-grouping-content"]'
        xp = f'//*[@class="info"]/h4[normalize-space(text())="{self.table_name}"]/ancestor::table'
        table_sel = response.xpath(xp)

        # upper body
        row_loaders = []
        tdl = TableDataLoader(selector=table_sel)
        tdl.base_url = response.url
        tdl.add_xpath('value', './/*[@class="info"]/h6/node()')
        tdl.add_xpath('value', './/*[@class="info"]/h4/span/node()')
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tdl = TableDataLoader(selector=table_sel)
        tdl.base_url = response.url
        tdl.add_xpath('value', './/*[@class="info"]/h5/node()')
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tdl = TableDataLoader(selector=table_sel)
        tdl.base_url = response.url
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tl.add_value('body', [row_loaders])

        # rest of body
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
