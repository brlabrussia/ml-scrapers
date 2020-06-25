import scrapy

from sentiment_ratings.items import RatingLoader


class SportsSpider(scrapy.Spider):
    name = 'sports'
    allowed_domains = ['sports.ru']

    def start_requests(self):
        url = 'https://www.sports.ru/betting/ratings/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.ratings-item__row')
        for sb in subject_blocks:
            subject_url = sb.css('.ratings-item__buttons a::attr(href)').get()
            yield response.follow(subject_url, self.parse_ratings)

    def parse_ratings(self, response):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', '.bookmaker-header-title__name::text')
        rl.add_value('all_min', 0.5)
        rl.add_value('all_max', 5)
        rl.add_xpath('experts', '//div[normalize-space(text())="Оценка Sports.ru"]/..//div[has-class("bets-stars")]/@data-rating')
        rl.add_xpath('users', '//div[normalize-space(text())="Оценка пользователей"]/..//div[has-class("bets-stars")]/@data-rating')
        rl.add_xpath('reliability', '//div[normalize-space(text())="Надежность"]/..//div[has-class("bets-stars")]/@data-rating')
        rl.add_xpath('variety', '//div[normalize-space(text())="Линии"]/..//div[has-class("bets-stars")]/@data-rating')
        rl.add_xpath('ratio', '//div[normalize-space(text())="Коэффициенты"]/..//div[has-class("bets-stars")]/@data-rating')
        rl.add_xpath('support', '//div[normalize-space(text())="Поддержка"]/..//div[has-class("bets-stars")]/@data-rating')
        yield rl.load_item()
