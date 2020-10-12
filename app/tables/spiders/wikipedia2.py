from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class Wikipedia2Spider(DefaultSpider):
    name = 'wikipedia2'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Клуб_Льва_Яшина']
    args = ['Состав Клуба Льва Яшина']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.args[0])
        xp = f'//*[@class="mw-headline"][normalize-space(text())="{self.args[0]}"]/ancestor::h2/following-sibling::table[has-class("sortable")][1]'
        table_sel = response.xpath(xp)

        # head
        for row_sel in [table_sel.css('tbody tr')[0]]:
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
        for row_sel in table_sel.css('tbody tr')[1:]:
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
