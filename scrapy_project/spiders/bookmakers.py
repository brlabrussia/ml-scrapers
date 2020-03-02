import datetime
import hashlib
import json
import urllib

import scrapy

from scrapy_project.items import Bookmaker


class BookmakersSpider(scrapy.Spider):
    name = "bookmakers"

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    has_more = True

    def start_requests(self):
        date = datetime.datetime.now().strftime("%d.%m.%Y")
        hash_ = hashlib.md5(f"metaratings.ru|{date}".encode()).hexdigest()
        limit = 100
        offset = 0

        # TODO: find better way to stop iteration
        while True:
            if not self.has_more:
                break
            params = {
                "iblock_id": 5,
                "hash": hash_,
                "limit": limit,
                "offset": offset,
            }
            url = "https://metaratings.ru/api/"
            url = f"{url}?{urllib.parse.urlencode(params)}"
            yield scrapy.Request(url)
            offset += limit

    def parse(self, response):
        response_json = json.loads(response.body)
        elements = response_json.get("elements")
        if not elements:
            self.has_more = False
            return
        for element in elements:
            bookmaker = Bookmaker()
            bookmaker["external_id"] = element.get("id")
            bookmaker["name"] = element.get("name")
            yield bookmaker
