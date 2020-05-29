from typing import Dict, List, Union
from urllib.parse import urlparse

import requests
from scrapy.exceptions import NotConfigured

ReviewData = Dict[str, Union[str, float, None]]


class WebhookPipeline:
    """
    Sends scraped posts in chunks (`spider.webhook_chunk_size`)
    to url (`spider.webhook_url`).

    If `spider.webhook_compat` is set, adapt schema before sending.
    If `spider.webhook_chunk_size` isn't set, it defaults to 1000,
    if `spider.webhook_url` isn't set, pipeline gets disabled.

    TODO stats for posts sent
    TODO switch to crawler settings instead of spider attrs
    """

    url: str
    chunk_size = 1000
    compat = False

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def __init__(self, spider):
        if hasattr(spider, 'webhook_url'):
            self.url = spider.webhook_url
        else:
            raise NotConfigured("webhook_url isn't set")

        if hasattr(spider, 'webhook_chunk_size'):
            self.chunk_size = int(spider.webhook_chunk_size)

        if hasattr(spider, 'webhook_compat'):
            self.compat = True

    def open_spider(self, spider):
        self.posts: List[ReviewData] = []
        self.client = requests.Session()

    def process_item(self, item, spider):
        post = dict(item)
        if self.compat:
            post = self.adapt_schema(post)
        self.posts.append(post)
        if len(self.posts) >= self.chunk_size:
            self.send_posts()
        return item

    def close_spider(self, spider):
        self.send_posts()
        self.client.close()

    def send_posts(self):
        self.client.post(self.url, json=self.posts)
        self.posts.clear()

    @staticmethod
    def adapt_schema(post: ReviewData) -> ReviewData:
        host_source_matches = {
            'apps.apple.com': 'Itunes.apple.com',
            'betonmobile.ru': 'Betonmobile',
            'bookmaker-ratings.ru': 'Рейтинг Букмекеров',
            'kushvsporte.ru': 'Kush v sporte',
            'legalbet.ru': 'Legalbet',
            'sports.ru': 'Sports.ru',
            'vseprosport.ru': 'ВсеПроСпорт.ру',
        }
        host = urlparse(post.get('url')).netloc.replace('www.', '')
        source = host_source_matches.get(host)

        return {
            'bookmaker': post.get('subject', ''),
            'comment': post.get('content_comment', ''),
            'content': post.get('content', ''),
            'create_dtime': post.get('time', ''),
            'minuses': post.get('content_negative', ''),
            'pluses': post.get('content_positive', ''),
            'rating': post.get('rating'),
            'source': source,
            'title': post.get('content_title', ''),
            'username': post.get('author', 'account is deleted'),  # bookmakerratings legacy
        }


class ImagesPipeline:
    pass
