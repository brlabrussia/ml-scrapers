from typing import Dict, List, Union
from urllib.parse import urlparse

import requests
from scrapy.exceptions import DropItem, NotConfigured

ReviewData = Dict[str, Union[str, float, None]]


class BuildContentPipeline:
    """
    Try to build `content` field from secondary fields: (`content_title`,
    `content_positive`, `content_negative` and `content_comment`), ~~pop them
    in the process~~.

    Drop item on failure.
    """

    def process_item(self, item, spider):
        def decorate_value(value: str, prefix: str) -> str:
            return f'"{prefix}": {value}\n\n' if value else ''

        if not item.get('content'):
            value_prefix_pairs = [
                # TODO pop unnecessary fields
                (item.get('content_title', None), 'Заголовок'),
                (item.get('content_positive', None), 'Плюсы'),
                (item.get('content_negative', None), 'Минусы'),
                (item.get('content_comment', None), 'Комментарий'),
            ]
            content = ''.join(decorate_value(v, p) for v, p in value_prefix_pairs)
            content = content.strip()
            if not content:
                raise DropItem("Can't build content")
            item['content'] = content
        return item


class WebhookPipeline:
    """
    Sends scraped posts in chunks (`spider.webhook_chunk_size`)
    to url (`spider.webhook_url`).

    If `spider.webhook_compat` is set, adapt schema before sending.
    If `spider.webhook_chunk_size` isn't set, it defaults to 1000,
    if `spider.webhook_url` isn't set, pipeline gets disabled.
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
            'bookmaker': post.get('subject'),
            'comment': post.get('content_comment'),
            'content': post.get('content'),
            'create_dtime': post.get('time'),
            'minuses': post.get('content_negative'),
            'pluses': post.get('content_positive'),
            'rating': post.get('rating'),
            'source': source,
            'title': post.get('content_title'),
            'username': post.get('author') or 'account is deleted',  # bookmakerratings legacy
        }
