import json
import re
from distutils.util import strtobool
from typing import Union
from urllib.parse import unquote

import scrapy
from furl import furl

from sentiment_ru.items import ReviewLoader


class ItunesSpider(scrapy.Spider):
    name = 'itunes'
    allowed_domains = ['apps.apple.com']
    custom_settings = {'CONCURRENT_REQUESTS': 2}
    crawl_deep = False
    crawl_depth = 500
    auth_token = None
    start_urls = [
        'https://apps.apple.com/ru/app/id1166619854',
        'https://apps.apple.com/ru/app/id1065803457',
        'https://apps.apple.com/ru/app/id1177395683',
        'https://apps.apple.com/ru/app/id1392323505',
        'https://apps.apple.com/ru/app/id1127251682',
        'https://apps.apple.com/ru/app/id1491142951',
        'https://apps.apple.com/ru/app/id1259203065',
        'https://apps.apple.com/ru/app/id1378876484',
        'https://apps.apple.com/ru/app/id1296163413',
        'https://apps.apple.com/ru/app/id1492307356',
        'https://apps.apple.com/ru/app/id1485980763',
        'https://apps.apple.com/ru/app/id1294769808',
        'https://apps.apple.com/ru/app/id1310600465',
        'https://apps.apple.com/ru/app/id1469527336',
        'https://apps.apple.com/ru/app/id1455333246',
        'https://apps.apple.com/ru/app/id1475084805',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_subject_info)

    def parse_subject_info(self, response):
        if not self.auth_token:
            self.auth_token = self.extract_auth_token(response)
        if not self.auth_token:
            return
        url = response.request.url
        xhr_url = self.build_xhr_url(url)
        if not xhr_url:
            return
        yield response.follow(
            url=xhr_url,
            headers={'authorization': f'Bearer {self.auth_token}'},
            callback=self.parse_reviews,
            cb_kwargs={
                'subject_url': unquote(url),
                'subject_name': response.css('.app-header__title::text').get(),
            },
        )

    def parse_reviews(self, response, subject_url: str, subject_name: str):
        response_json = json.loads(response.body)
        api_reviews = response_json.get('data')
        for ar in api_reviews:
            attrs = ar.get('attributes')
            rl = ReviewLoader()
            rl.add_value('id', ar.get('id'))
            rl.add_value('author', attrs.get('userName'))
            rl.add_value('content', attrs.get('review'))
            rl.add_value('content_title', attrs.get('title'))
            rl.add_value('language', 'ru')
            rl.add_value('rating', attrs.get('rating'))
            rl.add_value('rating_max', 5)
            rl.add_value('rating_min', 1)
            rl.add_value('subject', subject_name)
            rl.add_value('time', attrs.get('date'))
            rl.add_value('type', 'review')
            rl.add_value('url', subject_url)
            yield rl.load_item()

        offset_current = furl(response.request.url).args.get('offset')
        crawl_deep = strtobool(str(self.crawl_deep))
        want_more = crawl_deep or (int(offset_current) < self.crawl_depth)
        next_url = response_json.get('next')
        if want_more and next_url:
            f = furl(response.request.url)
            f.args['offset'] = furl(next_url).args['offset']
            yield response.request.replace(url=f.url)

    def extract_auth_token(self, response: scrapy.http.Response) -> str:
        """
        Extracts token required for XHRs from `scrapy.http.Response`.
        Response should be for main page of the app,
        for example https://apps.apple.com/us/app/id1108187098
        """
        css = 'meta[name="web-experience-app/config/environment"]::attr(content)'
        meta = response.css(css).get()
        try:
            meta = json.loads(unquote(meta))
            auth_token = meta.get('MEDIA_API').get('token')
            return auth_token
        except (TypeError, AttributeError) as error:
            self.logger.warning(f"can't extract auth_token\n{repr(error)}")
            return False

    def build_xhr_url(self, url: str) -> Union[str, bool]:
        """
        Builds URL for XHR from URL for main page of the app,
        for example https://apps.apple.com/us/app/id1108187098
        """
        try:
            lang = re.search(r'apple\.com/(\w+)/', url).group(1)
            app_id = re.search(r'/id(\d+)/?$', url).group(1)
        except AttributeError as error:
            self.logger.warning(f"can't build xhr_url\n{repr(error)}")
            return False
        f = furl(
            url=f'https://amp-api.apps.apple.com/v1/catalog/{lang}/apps/{app_id}/reviews',
            query={
                'l': 'en-US' if lang == 'us' else lang,
                'offset': 0,
                'platform': 'web',
                'additionalPlatforms': 'appletv,ipad,iphone,mac',
            },
        )
        return f.url
