import scrapy

from sentiment_ratings.items import RatingLoader


class BookmakerratingsSpider(scrapy.Spider):
    name = 'bookmakerratings'
    allowed_domains = ['bookmaker-ratings.ru']
    custom_settings = {'CONCURRENT_REQUESTS': 1}

    def start_requests(self):
        url = 'https://bookmaker-ratings.ru/bookmakers-homepage/vse-bukmekerskie-kontory/'
        yield scrapy.Request(url, callback=self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.table-container .table-row')
        for sb in subject_blocks:
            subject_name = sb.css('::attr(data-name)').get()
            subject_url = sb.css('.review-link::attr(href)').get()
            yield response.follow(
                subject_url,
                self.parse_items,
                cb_kwargs={'subject_name': subject_name},
            )

    def parse_items(self, response, subject_name):
        sel = (
            '//*[has-class("sub-item")]'
            '/*[has-class("sub-item-text")][starts-with(normalize-space(text()), "{}")]'
            '/following-sibling::strong[1]/text()'
        )
        rex = r'(.+)/'
        loader = RatingLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_value('subject', subject_name)
        loader.add_value('min', 1)
        loader.add_value('max', 5)
        loader.add_css('experts', '.section-review-top .rating-stars .cnt span::text')
        loader.add_css('users', '.section-review-top .user-rating .total-number::text', re=rex)
        loader.add_xpath('reliability', sel.format('Надежность'), re=rex)
        loader.add_xpath('variety', sel.format('Линия в прематче'), re=rex)
        loader.add_xpath('variety', sel.format('Линия в лайве'), re=rex)
        loader.add_xpath('ratio', sel.format('Коэффициенты'), re=rex)
        loader.add_xpath('withdrawal', sel.format('Удобство платежей'), re=rex)
        loader.add_xpath('support', sel.format('Служба поддержки'), re=rex)
        loader.add_xpath('bonuses', sel.format('Бонусы и акции'), re=rex)
        yield loader.load_item()
