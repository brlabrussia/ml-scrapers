import json

import scrapy
import w3lib.url
from scrapy.http import Response

from sentiment_ru.items import ReviewLoader


class SportsSpider(scrapy.Spider):
    name = "sports"
    allowed_domains = ["sports.ru"]

    def start_requests(self):
        url = "https://www.sports.ru/betting/ratings/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response: Response):
        xp = "//div[has-class('ratings-item__row')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_id = bookmaker_block.xpath(".//div[has-class('bets-stars')]/@data-id").get()
            bookmaker_url = "https://www.sports.ru"
            bookmaker_url += bookmaker_block.xpath(".//span[has-class('ratings-item__feedbacks')]/a/@href").get()

            params = {"args": f'{{"bookmaker_page_id":{bookmaker_id},"count":1000,"sort":"new"}}'}
            url = "https://www.sports.ru/core/bookmaker/opinion/get/"
            url = w3lib.url.add_or_replace_parameters(url, params)
            cb_kwargs = {"bookmaker_url": bookmaker_url}
            yield response.follow(url, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response: Response, bookmaker_url: str):
        response_json = json.loads(response.body)
        api_reviews = response_json.get("opinions")
        for api_review in api_reviews:
            loader = ReviewLoader()
            loader.add_value("author", api_review.get("user").get("name"))
            loader.add_value("content", api_review.get("content"))
            loader.add_value("rating", api_review.get("user_rating"))
            loader.add_value("rating_max", 5)
            loader.add_value("rating_min", 0.5)
            loader.add_value("subject", api_review.get("bookmaker").get("name"))
            loader.add_value("time", api_review.get("create_time").get("full"))
            loader.add_value("type", "review")
            loader.add_value("url", bookmaker_url)
            yield loader.load_item()
