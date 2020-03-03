import json
import urllib

import scrapy

from scrapy_project.items import ReviewLoader


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
            url = self.build_url_from_bookmaker_id(bookmaker_id)
            yield response.follow(url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        response_json = json.loads(response.body)
        api_reviews = response_json.get("opinions")
        for api_review in api_reviews:
            loader = ReviewLoader()

            loader.add_value("bookmaker", api_review.get("bookmaker").get("name"))
            loader.add_value("source", self.source_name)

            loader.add_value("content", api_review.get("content"))
            loader.add_value("title", "")
            loader.add_value("comment", "")
            loader.add_value("pluses", "")
            loader.add_value("minuses", "")

            loader.add_value("rating", api_review.get("user_rating"))
            loader.add_value("username", api_review.get("user").get("name"))
            loader.add_value("create_dtime", api_review.get("create_time").get("full"))

            yield loader.load_item()

    @staticmethod
    def build_url_from_bookmaker_id(bookmaker_id):
        params = {"args": f'{{"bookmaker_page_id":{bookmaker_id},"count":1000,"sort":"new"}}'}
        params_encoded = urllib.parse.urlencode(params)
        url = "https://www.sports.ru/core/bookmaker/opinion/get/" + "?" + params_encoded
        return url
