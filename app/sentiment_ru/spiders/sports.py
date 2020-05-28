import json

import scrapy
from furl import furl

from sentiment_ru.items import ReviewLoader


class SportsSpider(scrapy.Spider):
    name = 'sports'
    allowed_domains = ['sports.ru']

    def start_requests(self):
        url = 'https://www.sports.ru/betting/ratings/'
        yield scrapy.Request(url, self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.ratings-item__row')
        for sb in subject_blocks:
            subject_id = sb.css('.bets-stars::attr(data-id)').get()
            subject_url = sb.css('.ratings-item__feedbacks a::attr(href)').get()

            url = 'https://www.sports.ru/core/bookmaker/opinion/get/'
            query = {'args': f'{{"bookmaker_page_id":{subject_id},"count":1000,"sort":"new"}}'}
            yield response.follow(
                url=furl(url, query=query).url,
                callback=self.parse_reviews,
                cb_kwargs={'subject_url': subject_url},
            )

    def parse_reviews(self, response, subject_url: str):
        response_json = json.loads(response.body)
        api_reviews = response_json.get('opinions')
        for ar in api_reviews:
            rl = ReviewLoader()
            rl.add_value('id', ar.get('id'))
            rl.add_value('author', ar.get('user').get('name'))
            rl.add_value('content', ar.get('content'))
            rl.add_value('rating', ar.get('user_rating'))
            rl.add_value('rating_max', 5)
            rl.add_value('rating_min', 0.5)
            rl.add_value('subject', ar.get('bookmaker').get('name'))
            rl.add_value('time', ar.get('create_time').get('full'))
            rl.add_value('type', 'review')
            rl.add_value('url', response.urljoin(subject_url))
            yield rl.load_item()
