from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class IihfSpider(DefaultSpider):
    name = 'iihf'
    allowed_domains = ['iihf.com']
    start_urls = ['https://www.iihf.com/en/worldranking']
    args = ["2020 Men's World Ranking"]

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.args[0])
        xp = '//*[@class="s-title"][normalize-space(text())="{}"]/following-sibling::table[1]'
        table_sel = response.xpath(xp.format(self.args[0]))

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
