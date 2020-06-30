import scrapy

from sentiment_ratings.items import RatingLoader


class BookmakerratingsSpider(scrapy.Spider):
    name = 'bookmakerratings'
    allowed_domains = ['bookmaker-ratings.ru']
    custom_settings = {'CONCURRENT_REQUESTS': 4}

    def start_requests(self):
        url = 'https://bookmaker-ratings.ru/bookmakers-homepage/vse-bukmekerskie-kontory/'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.table-container .table-row')
        for sb in subject_blocks:
            subject_name = sb.css('::attr(data-name)').get()
            subject_url = sb.css('.review-link::attr(href)').get()
            yield response.follow(
                subject_url,
                self.parse_ratings,
                cb_kwargs={'subject_name': subject_name},
            )

    def parse_ratings(self, response, subject_name):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_value('subject', subject_name)
        rl.add_value('min', 1)
        rl.add_value('max', 5)
        rl.add_css('experts', '.section-review-top .rating-stars .cnt span::text')
        rl.add_css('users', '.section-review-top .user-rating .total-number::text', re=r'(.*)/')
        rl.add_xpath('reliability', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Надежность"]/..//*[has-class("cnt")]/span/text()')
        rl.add_xpath('variety', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Линия в прематче"]/..//*[has-class("cnt")]/span/text()')
        rl.add_xpath('ratio', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Коэффициенты"]/..//*[has-class("cnt")]/span/text()')
        rl.add_xpath('withdrawal', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Удобство платежей"]/..//*[has-class("cnt")]/span/text()')
        rl.add_xpath('support', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Служба поддержки"]/..//*[has-class("cnt")]/span/text()')
        rl.add_xpath('bonuses', '//*[@id="feedbacks"]//*[has-class("title")][normalize-space(text())="Бонусы и акции"]/..//*[has-class("cnt")]/span/text()')
        yield rl.load_item()
