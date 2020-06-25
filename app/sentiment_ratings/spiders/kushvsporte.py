import scrapy

from sentiment_ratings.items import RatingLoader


class KushvsporteSpider(scrapy.Spider):
    name = 'kushvsporte'
    allowed_domains = ['kushvsporte.ru']

    def start_requests(self):
        url = 'https://kushvsporte.ru/bookmaker/rating'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.blockBkList > *')
        for sb in subject_blocks:
            subject_name = sb.css('h3::text').get()
            subject_url = sb.css('a.btn-default::attr(href)').get()
            yield response.follow(
                subject_url,
                self.parse_ratings,
                cb_kwargs={'subject_name': subject_name},
            )

    def parse_ratings(self, response, subject_name):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_value('subject', subject_name)
        rl.add_value('all_min', 1)
        rl.add_value('all_max', 5)
        rl.add_css('users', '.iconinfoPageBK .ratingStarsCaption span::text')
        rl.add_xpath('reliability', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Надежность"]/..//*[has-class("lbrating")]/text()')
        rl.add_xpath('variety', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Линия в прематче"]/..//*[has-class("lbrating")]/text()')
        rl.add_xpath('ratio', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Коэффициенты"]/..//*[has-class("lbrating")]/text()')
        rl.add_xpath('withdrawal', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Удобство платежей"]/..//*[has-class("lbrating")]/text()')
        rl.add_xpath('support', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Служба поддержки"]/..//*[has-class("lbrating")]/text()')
        rl.add_xpath('bonuses', '//div[has-class("blockBKProgress")]/div[normalize-space(text())="Бонусы и акции"]/..//*[has-class("lbrating")]/text()')
        yield rl.load_item()
