from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class UfcSpider(DefaultSpider):
    name = 'ufc'
    allowed_domains = ['bsrussia.com']
    start_urls = ['https://ru.ufc.com/rankings']
    args = ['Полусредний вес']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.args[0])
        # xp = f'//*[@class="view-grouping-header"][normalize-space(text())="{self.args[0]}"]/following-sibling::*[@class="view-grouping-content"]'
        xp = f'//*[@class="info"]/h4[normalize-space(text())="{self.args[0]}"]/ancestor::table'
        table_sel = response.xpath(xp)

        # upper body
        row_loaders = []
        tdl = TableDataLoader(selector=table_sel)
        tdl.add_xpath('value', './/*[@class="info"]/h6/node()')
        tdl.add_xpath('value', './/*[@class="info"]/h4/span/node()')
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tdl = TableDataLoader(selector=table_sel)
        tdl.add_xpath('value', './/*[@class="info"]/h5/node()')
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tdl = TableDataLoader(selector=table_sel)
        tdl.add_value('value', '')
        row_loaders.append(tdl)
        tl.add_value('body', [row_loaders])

        # rest of body
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
