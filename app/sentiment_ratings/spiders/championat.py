import scrapy

from sentiment_ratings.items import ChampionatLoader


class ChampionatSpider(scrapy.Spider):
    name = 'championat'
    allowed_domains = ['championat.com']

    def start_requests(self):
        url = 'https://bet.championat.com/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.table-bookmaker__tr')
        for sb in subject_blocks:
            subject_url = sb.css('.table-bookmaker__link a::attr(href)').get()
            yield response.follow(subject_url, self.parse_items)

    def parse_items(self, response):
        sel = (
            '//*[has-class("block-bookmaker-info__option-title")][starts-with(normalize-space(text()), "{}")]'
            '/../..//*[has-class("block-bookmaker-info__option-rating")]/@class'
        )
        loader = ChampionatLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_css('subject', '.block-bookmaker-info__title *::text')
        loader.add_value('min', 0)
        loader.add_value('max', 100)
        loader.add_css('experts', '.block-bookmaker-info__description .rating-star-list::attr(data-rating)')
        loader.add_xpath('variety', sel.format('Выбор ставок'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        loader.add_xpath('bonuses', sel.format('Бонусы и фрибеты'))
        yield loader.load_item()
