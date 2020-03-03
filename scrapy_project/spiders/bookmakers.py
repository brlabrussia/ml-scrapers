import datetime
import hashlib
import json
import urllib

import scrapy

from scrapy_project.items import Bookmaker


class BookmakersSpider(scrapy.Spider):
    name = "bookmakers"
    allowed_domains = ["metaratings.ru"]
    custom_settings = {"ITEM_PIPELINES": None}

    def start_requests(self):
        date = datetime.datetime.now().strftime("%d.%m.%Y")
        hash_ = hashlib.md5(f"metaratings.ru|{date}".encode()).hexdigest()
        params = {
            "iblock_id": 5,
            "hash": hash_,
            "limit": 100,
            "offset": 0,
        }
        url = self.build_url_from_params(params)
        yield scrapy.Request(url, cb_kwargs={"params": params})

    def parse(self, response, params):
        response_json = json.loads(response.body)
        elements = response_json.get("elements")
        for element in elements:
            bookmaker = Bookmaker()
            bookmaker["external_id"] = element.get("id")
            bookmaker["name"] = element.get("name")
            yield bookmaker

        next_offset = response_json.get("offset") + response_json.get("limit")
        has_more = response_json.get("count") > next_offset
        if has_more:
            params["offset"] = next_offset
            url = self.build_url_from_params(params)
            yield response.follow(url, callback=self.parse, cb_kwargs={"params": params})

    @staticmethod
    def build_url_from_params(params):
        params_encoded = urllib.parse.urlencode(params)
        url = "https://metaratings.ru/api/" + "?" + params_encoded
        return url
