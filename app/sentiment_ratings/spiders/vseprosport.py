import scrapy

from sentiment_ratings.items import RatingLoader


class VseprosportSpider(scrapy.Spider):
    name = 'vseprosport'
    allowed_domains = ['vseprosport.ru']

    def start_requests(self):
        url = 'https://www.vseprosport.ru/reyting-bukmekerov/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.bookmeker_table_offer')
        for sb in subject_blocks:
            subject_name = sb.css('.bookmeker_table_offer_logo img::attr(title)').get()
            subject_url = sb.css('.bookmeker_table_offer_button a::attr(href)').get()
            yield response.follow(
                subject_url,
                self.parse_ratings,
                cb_kwargs={'subject_name': subject_name},
            )

    def parse_ratings(self, response, subject_name):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_value('subject', subject_name)
        rl.add_value('min', 0)
        rl.add_value('max', 5)
        rl.add_css('experts', '.bookmaker_bonus_header_item_star p::text', re=r'(.*)/')
        rl.add_xpath('users', '//*[has-class("bookmaker_comments_header")]//*[has-class("icon-star-gold")]/../text()[1]')
        rl.add_xpath('reliability', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Надежность"]/../b/text()')
        rl.add_xpath('variety', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Линия в прематче"]/../b/text()')
        rl.add_xpath('ratio', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Коэффициенты"]/../b/text()')
        rl.add_xpath('withdrawal', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Удобство платежей"]/../b/text()')
        rl.add_xpath('support', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Служба поддержки"]/../b/text()')
        rl.add_xpath('bonuses', '//*[has-class("bookmaker_bonus_header_specification_item_name")]/p[normalize-space(text())="Бонусы и акции"]/../b/text()')
        yield rl.load_item()
