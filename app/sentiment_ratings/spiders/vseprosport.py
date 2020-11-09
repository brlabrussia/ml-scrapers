import scrapy

from sentiment_ratings.items import RatingLoader


class VseprosportSpider(scrapy.Spider):
    name = 'vseprosport'
    allowed_domains = ['vseprosport.ru']

    def start_requests(self):
        url = 'https://www.vseprosport.ru/reyting-bukmekerov/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        subject_blocks = response.css('.bookmakers-list .list-item')
        for sb in subject_blocks:
            subject = sb.css('.img::attr(title)').get()
            urls = sb.css('a::attr(href)').re(r'/reyting-bukmekerov/\w+/?')
            if not urls:
                continue
            url = urls[0]
            yield response.follow(
                url,
                self.parse_items,
                cb_kwargs={'subject': subject},
            )

    def parse_items(self, response, subject):
        sel = (
            '//*[has-class("bookmaker_bonus_header_specification_item_name")]'
            '/p[normalize-space(text())="{}"]/../b/text()'
        )
        loader = RatingLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_value('subject', subject)
        loader.add_value('min', 0)
        loader.add_value('max', 5)
        loader.add_css('experts', '.bookmaker_bonus_header_item_star p::text', re=r'(.*)/')
        loader.add_xpath('users', '//*[has-class("bookmaker_comments_header")]//*[has-class("icon-star-gold")]/../text()[1]')
        loader.add_xpath('reliability', sel.format('Надежность'))
        loader.add_xpath('variety', sel.format('Линия в прематче'))
        loader.add_xpath('variety', sel.format('Линия в лайве'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        loader.add_xpath('withdrawal', sel.format('Удобство платежей'))
        loader.add_xpath('support', sel.format('Служба поддержки'))
        loader.add_xpath('bonuses', sel.format('Бонусы и акции'))
        yield loader.load_item()
