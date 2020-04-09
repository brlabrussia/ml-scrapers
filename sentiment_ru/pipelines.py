from typing import List

import requests
from scrapy.exceptions import DropItem, NotConfigured


class BuildContentPipeline(object):
    '''
    Try to build `content` field from secondary fields: (`content_title`,
    `content_positive`, `content_negative` and `content_comment`), pop them
    in the process.

    Drop item on failure.
    '''

    def process_item(self, item, spider):

        def decorate_value(value: str, prefix: str) -> str:
            return f'"{prefix}": {value}\n\n' if value else ''

        if not item.get('content'):
            value_prefix_pairs = [
                (item.pop('content_title', None), 'Заголовок'),
                (item.pop('content_positive', None), 'Плюсы'),
                (item.pop('content_negative', None), 'Минусы'),
                (item.pop('content_comment', None), 'Комментарий'),
            ]
            content = ''.join(
                decorate_value(v, p) for v, p in value_prefix_pairs)
            content = content.strip()
            if not content:
                raise DropItem("Can't build content")
            item['content'] = content
        return item


class WebhookPipeline(object):
    '''
    Sends scraped posts in chunks (`spider.webhook_chunk_size`)
    to url (`spider.webhook_url`).

    If `spider.webhook_chunk_size` isn't set, it defaults to 1000,
    if `spider.webhook_url` isn't set, pipeline gets disabled.
    '''

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
        else:
            self.chunk_size = 1000

    def open_spider(self, spider):
        self.posts: List[dict] = []
        self.client = requests.Session()

    def process_item(self, item, spider):
        self.posts.append(dict(item))
        if len(self.posts) >= self.chunk_size:
            self.send_posts()
        return item

    def close_spider(self, spider):
        self.send_posts()
        self.client.close()

    def send_posts(self):
        self.client.post(self.url, json=self.posts)
        self.posts.clear()
