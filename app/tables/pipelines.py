import logging
from typing import Dict, List

import requests
from scrapy.exceptions import NotConfigured


class WebhookPipeline:
    def __init__(self, stats, endpoint, chunk_size, instance_id):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.stats = stats
        self.endpoint = endpoint
        self.chunk_size = chunk_size
        self.instance_id = instance_id

    @classmethod
    def from_crawler(cls, crawler):
        endpoint = (
            getattr(crawler.spider, 'webhook_url', None) or
            crawler.settings.get('WEBHOOK_ENDPOINT')
        )
        if not endpoint:
            raise NotConfigured('endpoint_not_set')

        chunk_size = (
            getattr(crawler.spider, 'webhook_chunk_size', None) or
            crawler.settings.getint('WEBHOOK_CHUNK_SIZE', 1000)
        )
        chunk_size = int(chunk_size)  # compatibility with old configuration

        instance_id = int(getattr(crawler.spider, 'instance_id'))

        return cls(crawler.stats, endpoint, chunk_size, instance_id)

    def open_spider(self, spider):
        self.logger.debug(
            'Started: %s',
            {
                'endpoint': self.endpoint,
                'chunk_size': self.chunk_size,
            },
        )
        self.items: List[Dict] = []
        self.client = requests.Session()

    def process_item(self, item, spider):
        post = dict(item)
        self.items.append(post)
        if len(self.items) >= self.chunk_size:
            self.send_items()
        return item

    def close_spider(self, spider):
        self.send_items()
        self.client.close()

    def send_items(self):
        response = self.client.post(self.endpoint, json={'instance_id': self.instance_id, 'result': self.items[0]})
        self.stats.inc_value('webhook/items_count', len(self.items))
        if response.ok:
            self.stats.inc_value('webhook/response_count')
        self.stats.inc_value(f'webhook/response_status_count/{response.status_code}')
        self.items.clear()
