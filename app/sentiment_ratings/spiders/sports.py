import scrapy

from sentiment_ratings.items import RatingLoader


class SportsSpider(scrapy.Spider):
    name = 'sports'
    allowed_domains = ['sports.ru']

    def start_requests(self):
        url = 'https://www.sports.ru/betting/ratings/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.ratings-item__row')
        for sb in subject_blocks:
            url = sb.css('.ratings-item__buttons a::attr(href)').get()
            yield response.follow(url, self.parse_items)

    def parse_items(self, response):
        sel = (
            '//div[normalize-space(text())="{}"]'
            '/..//div[has-class("bets-stars")]/@data-rating'
        )
        loader = RatingLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_css('subject', '.bookmaker-header-title__name::text')
        loader.add_value('min', 0.5)
        loader.add_value('max', 5)
        loader.add_xpath('experts', sel.format('Оценка Sports.ru'))
        loader.add_xpath('users', sel.format('Оценка пользователей'))
        loader.add_xpath('reliability', sel.format('Надежность'))
        loader.add_xpath('variety', sel.format('Линии'))
        loader.add_xpath('variety', sel.format('Live'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        loader.add_xpath('support', sel.format('Поддержка'))
        yield loader.load_item()
