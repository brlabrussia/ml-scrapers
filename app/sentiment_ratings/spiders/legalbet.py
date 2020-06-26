import scrapy

from sentiment_ratings.items import RatingLoader


class LegalbetSpider(scrapy.Spider):
    name = 'legalbet'
    allowed_domains = ['legalbet.ru']

    def start_requests(self):
        url = 'https://legalbet.ru/bukmekerskye-kontory/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('[data-book-details-toggle]:not([class])')
        for sb in subject_blocks:
            subject_link = sb.css('a[title=Отзывы]::attr(href)').get().replace('/feedback/', '/bukmekerskye-kontory/')
            yield response.follow(subject_link, self.parse_ratings)

    def parse_ratings(self, response):
        def get_rating_for_field(field):
            xp = f'//*[has-class("bookmaker-score")]//h2[starts-with(normalize-space(text()), "{field}")]/@class'
            classes = response.xpath(xp).get()
            if 'good' in classes:
                return 5
            elif 'medium' in classes:
                return 2.5
            elif 'bad' in classes:
                return 0

        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', '.bookmaker-info-block .block-section.heading::text', re=r'\w+')
        rl.add_value('all_min', 0)
        rl.add_value('all_max', 5)
        rl.add_value('variety', get_rating_for_field('Выбор ставок'))
        rl.add_value('ratio', get_rating_for_field('Коэффициенты'))
        yield rl.load_item()
