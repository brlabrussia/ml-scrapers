import json

import scrapy
import w3lib.url

from sentiment_ru.items import ReviewLoader


class SportsSpider(scrapy.Spider):
    name = "sports"
    source_name = "Sports.ru"
    allowed_domains = ["sports.ru"]

    def start_requests(self):
        url = "https://www.sports.ru/betting/ratings/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//div[has-class('ratings-item__row')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_id = bookmaker_block.xpath(".//div[has-class('bets-stars')]/@data-id").get()

            params = {"args": f'{{"bookmaker_page_id":{bookmaker_id},"count":1000,"sort":"new"}}'}
            url = "https://www.sports.ru/core/bookmaker/opinion/get/"
            url = w3lib.url.add_or_replace_parameters(url, params)
            yield response.follow(url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        response_json = json.loads(response.body)
        api_reviews = response_json.get("opinions")
        for api_review in api_reviews:
            loader = ReviewLoader()
            loader.add_value("source", self.source_name)
            loader.add_value("bookmaker", api_review.get("bookmaker").get("name"))
            loader.add_value("rating", api_review.get("user_rating"))
            loader.add_value("username", api_review.get("user").get("name"))
            loader.add_value("create_dtime", api_review.get("create_time").get("full"))
            loader.add_value("content", api_review.get("content"))
            yield loader.load_item()
