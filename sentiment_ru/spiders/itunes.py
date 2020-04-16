import json
import re
from typing import Union
from urllib.parse import unquote

import scrapy
import w3lib.url
from scrapy.exceptions import CloseSpider

from sentiment_ru.items import ReviewLoader


class ItunesSpider(scrapy.Spider):
    name = "itunes"
    allowed_domains = ["apps.apple.com"]
    custom_settings = {"CONCURRENT_REQUESTS": 2}
    crawl_deep = False
    crawl_depth = 500
    auth_token = None

    def start_requests(self):
        # placeholder for testing until we get proper urls
        urls = [
            "https://apps.apple.com/us/app/pythonista-3/id1085978097",
            "https://apps.apple.com/ru/app/тануки-доставка-роллов-суши/id934422052",
            "https://apps.apple.com/ru/app/лига-ставок-ставки-на-спорт/id1065803457/",
        ]
        for url in urls:
            yield scrapy.Request(url, self.parse_subject_info)

    def parse_subject_info(self, response):
        # `True` either if it's first subject for current crawling session
        # or previous `extract_auth_token()` tries were unsuccessful
        if not self.auth_token:
            self.auth_token = self.extract_auth_token(response)

        url = response.request.url
        xhr_url = self.build_xhr_url(url)
        if not xhr_url:
            return
        cb_kwargs = {
            "subject_url": unquote(url),
            "subject_name": response.css(".app-header__title::text").get(),
        }
        yield response.follow(
            xhr_url,
            self.parse_reviews,
            cb_kwargs=cb_kwargs,
            headers={"authorization": f"Bearer {self.auth_token}"},
        )

    def parse_reviews(self, response, subject_url: str, subject_name: str):
        response_json = json.loads(response.body)
        api_reviews = response_json.get("data")
        for ar in api_reviews:
            attrs = ar.get("attributes")
            loader = ReviewLoader()
            loader.add_value("author", attrs.get("userName"))
            loader.add_value("content", attrs.get("review"))
            loader.add_value("content_title", attrs.get("title"))
            loader.add_value("rating", attrs.get("rating"))
            loader.add_value("rating_max", 5)
            loader.add_value("rating_min", 1)
            loader.add_value("subject", subject_name)
            loader.add_value("time", attrs.get("date"))
            loader.add_value("type", "review")
            loader.add_value("url", subject_url)
            yield loader.load_item()

        offset_current = w3lib.url.url_query_parameter(response.request.url, "offset")
        want_more = self.crawl_deep or (int(offset_current) < self.crawl_depth)
        next_url = response_json.get("next")
        if want_more and next_url:
            # mandatory params which for some reason are missing in API response
            params = {
                "platform": "web",
                "additionalPlatforms": "appletv,ipad,iphone,mac",
            }
            next_url = w3lib.url.add_or_replace_parameters(next_url, params)
            cb_kwargs = {"subject_url": subject_url, "subject_name": subject_name}
            yield response.follow(
                next_url,
                self.parse_reviews,
                cb_kwargs=cb_kwargs,
                headers={"authorization": f"Bearer {self.auth_token}"},
            )

    def extract_auth_token(self, response: scrapy.http.Response) -> str:
        """
        Extracts token required for XHRs from `scrapy.http.Response`.
        Response should be for main page of the app,
        for example https://apps.apple.com/us/app/mail/id1108187098
        """
        css = "meta[name='web-experience-app/config/environment']::attr(content)"
        meta = response.css(css).get()
        try:
            meta = json.loads(unquote(meta))
            auth_token = meta.get("MEDIA_API").get("token")
            return auth_token
        except (TypeError, AttributeError) as error:
            raise CloseSpider(f"can't extract auth_token\n{repr(error)}")

    def build_xhr_url(self, url: str) -> Union[str, bool]:
        """
        Builds URL for XHR from URL for main page of the app,
        for example https://apps.apple.com/us/app/mail/id1108187098
        """
        try:
            lang = re.search(r"apple\.com/(\w+)/", url).group(1)  # type: ignore
            app_id = re.search(r"/id(\d+)/?$", url).group(1)  # type: ignore
        except AttributeError as error:
            self.logger.warning(f"can't build xhr_url\n{repr(error)}")
            return False
        xhr_url = (
            f"https://amp-api.apps.apple.com/v1/catalog/{lang}/apps/{app_id}/reviews"
        )
        # following params are mandatory
        params = {
            "l": "en-US" if lang == "us" else lang,
            "offset": 0,
            "platform": "web",
            "additionalPlatforms": "appletv,ipad,iphone,mac",
        }
        xhr_url = w3lib.url.add_or_replace_parameters(xhr_url, params)
        return xhr_url
