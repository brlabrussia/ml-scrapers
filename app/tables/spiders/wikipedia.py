import bleach
import scrapy
from scrapy.loader.processors import Compose

from default.utils import StartUrlsMixin
from tables.items_ import TableDataLoader, TableLoader
from tables.utils import BASIC_POST_PROCESSOR, prepare_table_selector


class WikipediaSpider(StartUrlsMixin, scrapy.Spider):
    name = 'wikipedia'
    allowed_domains = ['wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Рейтинг_WBC']
    table_name = 'Первый тяжёлый вес'

    post_processor = Compose(
        BASIC_POST_PROCESSOR,
        lambda x: x.replace('<img', '<img style="display:inline;"'),
    )

    def parse(self, response):
        tl = TableLoader(response=response)
        tl.add_value('url', response.url)
        tl.add_value('title', self.table_name)
        xp = f'//*[@class="mw-headline"][normalize-space(text())="{self.table_name}"]/ancestor::h2/following-sibling::table[1]'
        table_sel = response.xpath(xp)
        table_sel = prepare_table_selector(
            table_sel,
            response,
            post_processor=self.post_processor,
        )

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
                tdl.add_value('style', 'text-align:left')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.css('tbody tr')[1:]:
            row_loaders = []
            for index, data_sel in enumerate(row_sel.css('td')):
                tdl = TableDataLoader(selector=data_sel)
                tdl.base_url = response.url
                value = data_sel.xpath('./node()').get()
                if index == 1:
                    value = bleach.clean(value, tags=[], strip=True).title()
                tdl.add_value('value', value)
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                tdl.add_value('style', 'text-align:left')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        yield tl.load_item()
