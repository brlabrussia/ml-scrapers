import requests
from scrapy.exceptions import DropItem

from sentiment_ru.settings import WEBHOOK_CHUNK_SIZE, WEBHOOK_URLS


class BuildContentPipeline(object):
    """
    Try to build `content` field from secondary fields: (`content_title`, `content_comment`,
    `content_positive` and `content_negative`), pop them in the process.
    Drop item on failure.
    """

    def process_item(self, item, spider):
        def decorate_value(value, prefix):
            return f'"{prefix}": {value}\n\n' if value else ""

        if not item.get("content"):
            value_prefix_pairs = [
                (item.pop("content_title", None), "Заголовок"),
                (item.pop("content_positive", None), "Плюсы"),
                (item.pop("content_negative", None), "Минусы"),
                (item.pop("content_comment", None), "Комментарий"),
            ]
            content = "".join(decorate_value(v, p) for v, p in value_prefix_pairs)
            content = content.strip()
            if not content:
                raise DropItem("Can't build content")
            item["content"] = content
        return item


class WebhookPipeline(object):
    """
    Sends scraped posts in chunks (`WEBHOOK_CHUNK_SIZE`) to urls (`WEBHOOK_URLS`).
    """

    chunk_size = WEBHOOK_CHUNK_SIZE

    def open_spider(self, spider):
        self.posts = []
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
        for url in WEBHOOK_URLS:
            self.client.post(url, json=self.posts)
        self.posts.clear()
