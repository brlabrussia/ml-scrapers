import scrapy

from sentiment_ratings.items import RatingLoader


class KushvsporteSpider(scrapy.Spider):
    name = 'kushvsporte'
    allowed_domains = ['kushvsporte.ru']

    def start_requests(self):
        url = 'https://kushvsporte.ru/bookmaker/rating'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.blockBkList > *')
        for sb in subject_blocks:
            subject = sb.css('h3::text').get()
            url = sb.css('a.btn-default::attr(href)').get()
            yield response.follow(
                url,
                self.parse_items,
                cb_kwargs={'subject': subject},
            )

    def parse_items(self, response, subject):
        sel = (
            '//div[has-class("blockBKProgress")]'
            '/div[normalize-space(text())="{}"]'
            '/..//*[has-class("lbrating")]/text()'
        )
        loader = RatingLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_value('subject', subject)
        loader.add_value('min', 1)
        loader.add_value('max', 5)
        loader.add_css('users', '.iconinfoPageBK .ratingStarsCaption span::text')
        loader.add_xpath('reliability', sel.format('Надежность'))
        loader.add_xpath('variety', sel.format('Линия в прематче'))
        loader.add_xpath('variety', sel.format('Линия в лайве'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        loader.add_xpath('withdrawal', sel.format('Удобство платежей'))
        loader.add_xpath('support', sel.format('Служба поддержки'))
        loader.add_xpath('bonuses', sel.format('Бонусы и акции'))
        yield loader.load_item()
