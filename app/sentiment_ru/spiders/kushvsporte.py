import json
from distutils.util import strtobool

import scrapy

from sentiment_ru.items import ReviewLoader


class KushvsporteSpider(scrapy.Spider):
    name = 'kushvsporte'
    allowed_domains = ['kushvsporte.ru']
    crawl_deep = False

    def start_requests(self):
        url = 'https://kushvsporte.ru/bookmaker/rating'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.blockBkList > *')
        for sb in subject_blocks:
            subject_name = sb.css('h3::text').get()
            subject_url = sb.css('a.medium::attr(href)').get()
            yield response.follow(
                subject_url,
                self.parse_reviews,
                cb_kwargs={'subject_name': subject_name},
            )

    def parse_reviews(self, response, subject_name: str):
        review_blocks = response.css('#reviews-block > .review')
        for rb in review_blocks:
            rl = ReviewLoader(selector=rb)
            rl.add_css('id', '[itemprop=reviewBody] > div::attr(id)', re=r'review(\d+)$')
            rl.add_css('author', '.infoUserRevievBK [itemprop=name]::attr(title)')
            rl.add_css('content_positive', '[itemprop=reviewBody] p:nth-of-type(1)::text')
            rl.add_css('content_negative', '[itemprop=reviewBody] p:nth-of-type(2)::text')
            rl.add_css('content_comment', '[itemprop=reviewBody] p:nth-of-type(3)::text')
            rl.add_css('rating', '[itemprop=ratingValue]::attr(content)')
            rl.add_value('rating_max', 5)
            rl.add_value('rating_min', 1)
            rl.add_value('subject', subject_name)
            rl.add_css('time', '[itemprop=datePublished]::attr(datetime)')
            rl.add_value('type', 'review')
            rl.add_value('url', response.url)
            yield rl.load_item()

        css = '#list-reviews-pagination:not([data-urls="[]"])::attr(data-urls)'
        next_page = response.css(css).get()
        if strtobool(str(self.crawl_deep)) and next_page:
            next_page = json.loads(next_page)[0]
            cb_kwargs = {'subject_name': subject_name}
            yield response.follow(
                next_page,
                self.parse_reviews,
                cb_kwargs=cb_kwargs,
            )
