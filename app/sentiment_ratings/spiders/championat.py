import scrapy

from sentiment_ratings.items import RatingLoader


class ChampionatSpider(scrapy.Spider):
    name = 'championat'
    allowed_domains = ['championat.com']

    def start_requests(self):
        url = 'https://bet.championat.com/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.table-bookmaker__tr')
        for sb in subject_blocks:
            subject_url = sb.css('.table-bookmaker__link a::attr(href)').get()
            yield response.follow(subject_url, self.parse_ratings)

    def parse_ratings(self, response):
        def get_rating_for_field(field):
            xp = f'//*[has-class("block-bookmaker-info__option-title")][starts-with(normalize-space(text()), "{field}")]/../..//*[has-class("block-bookmaker-info__option-rating")]/@class'
            classes = response.xpath(xp).get()
            if '_good' in classes:
                return 5
            elif '_middle' in classes:
                return 2.5
            elif '_bad' in classes:
                return 0

        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', '.block-bookmaker-info__title::text')
        rl.add_value('min', 0)
        rl.add_value('max', 5)
        rl.add_css('experts', '.block-bookmaker-info__description .rating-star-list::attr(data-rating)')
        rl.add_value('variety', get_rating_for_field('Выбор ставок'))
        rl.add_value('ratio', get_rating_for_field('Коэффициенты'))
        rl.add_value('bonuses', get_rating_for_field('Бонусы и фрибеты'))
        yield rl.load_item()
