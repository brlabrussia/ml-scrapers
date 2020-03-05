import datetime
import hashlib
import json

import scrapy
import w3lib.url


class MetaratingsSpider(scrapy.Spider):
    name = "metaratings"
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
        url = "https://metaratings.ru/api/"
        url = w3lib.url.add_or_replace_parameters(url, params)
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        response_json = json.loads(response.body)
        elements = response_json.get("elements")
        for element in elements:
            yield {
                "id": element.get("id"),
                "name": element.get("name"),
            }

        # Check whether more is available, prepare url
        url = response.request.url
        limit = int(w3lib.url.url_query_parameter(url, "limit"))
        offset = int(w3lib.url.url_query_parameter(url, "offset"))
        next_offset = offset + limit
        has_more = response_json.get("count") > next_offset
        if has_more:
            url = w3lib.url.add_or_replace_parameter(url, "offset", next_offset)
            yield response.follow(url, callback=self.parse_bookmakers)
