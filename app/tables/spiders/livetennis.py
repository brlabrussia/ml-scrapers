import scrapy

from tables.items import TableDataLoader, TableLoader


class LivetennisSpider(scrapy.Spider):
    name = 'livetennis'
    allowed_domains = ['live-tennis.eu']
    start_urls = ['https://live-tennis.eu/ru/official-atp-ranking']

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_css('title', '#plyrRankings caption::text')
        table_sel = response.xpath('//*[@id="plyrRankings"]/table/caption/parent::node()')

        # head
        for row_sel in table_sel.css('thead tr'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                tdl.add_xpath('value', './node()')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                tdl.add_xpath('width', './@width')
                tdl.add_xpath('height', './@height')
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
                tdl.add_xpath('width', './@width')
                tdl.add_xpath('height', './@height')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
