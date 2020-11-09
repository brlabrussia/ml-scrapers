import scrapy

from sentiment_ratings.items import LegalbetLoader


class LegalbetSpider(scrapy.Spider):
    name = 'legalbet'
    allowed_domains = ['legalbet.ru']

    def start_requests(self):
        url = 'https://legalbet.ru/rating-reliability/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.bookmakers-rating-reliability-table .js-link')
        for sb in subject_blocks:
            url = sb.css('::attr(data-href)').get()
            reliability = sb.css('.reliability-score::text').get()
            yield response.follow(
                url,
                self.parse_items,
                cb_kwargs={'reliability': reliability},
            )

    def parse_items(self, response, reliability):
        sel = (
            '//*[has-class("bookmaker-score")]'
            '//h2[starts-with(normalize-space(text()), "{}")]/@class'
        )
        loader = LegalbetLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_css('subject', '.bookmaker-info-block .block-section.heading::text', re=r'\w+')
        loader.add_value('min', 0)
        loader.add_value('max', 100)
        loader.add_value('reliability', reliability, re=r'(.+)%')
        loader.add_xpath('variety', sel.format('Выбор ставок'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        yield loader.load_item()
