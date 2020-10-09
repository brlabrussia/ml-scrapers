from tables.items import TableDataLoader, TableLoader
from tables.spiders.default import DefaultSpider


class HltvSpider(DefaultSpider):
    name = 'hltv'
    allowed_domains = ['hltv.org']
    start_urls = ['https://www.hltv.org/ranking/teams/']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '.regional-ranking-header::text')

        # yes
        for row_sel in response.css('.ranked-team'):
            row_loaders = []
            sels = [
                '.position',
                '.team-logo',
                '.teamLine .name',
                '.teamLine .points',
                '.playersLine',
            ]
            for sel in sels:
                data_sel = row_sel.css(sel)
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
