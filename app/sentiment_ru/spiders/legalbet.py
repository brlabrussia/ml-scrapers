from distutils.util import strtobool

import scrapy

from sentiment_ru.items import ReviewLoader


class LegalbetSpider(scrapy.Spider):
    name = 'legalbet'
    allowed_domains = ['legalbet.ru']
    crawl_deep = False

    def start_requests(self):
        url = 'https://legalbet.ru/bukmekerskye-kontory/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('[data-book-details-toggle]:not([class])')
        for sb in subject_blocks:
            subject_link = sb.css('a[title=Отзывы]::attr(href)').get()
            yield response.follow(subject_link, self.parse_reviews)

    def parse_reviews(self, response):
        subject_name = response.css('div.title > a::text').get()
        review_blocks = response.css('div.review')
        for rb in review_blocks:
            rl = ReviewLoader(selector=rb)
            rl.add_css('id', '::attr(id)', re=r'\d+$')
            rl.add_css('author', '.author a.name::text')
            rl.add_css('content_positive', '.icon-plus + .description::text')
            rl.add_css('content_negative', '.icon-minus + .description::text')
            rl.add_value('subject', subject_name)
            rl.add_css('time', '.author .date::text')
            rl.add_value('type', 'review')
            rl.add_value('url', response.url)
            yield rl.load_item()

        css = '[data-container-id=infinite-list]::attr(data-url)'
        next_page = response.css(css).get()
        if strtobool(str(self.crawl_deep)) and next_page:
            yield response.follow(next_page, self.parse_reviews)
