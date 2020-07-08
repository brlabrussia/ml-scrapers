import logging
from typing import Dict, List
from urllib.parse import urlparse

import requests
from furl import furl
from scrapy.exceptions import DropItem, NotConfigured
from scrapy.pipelines.images import ImagesPipeline as ImagesPipeline_


class WebhookPipeline:
    def __init__(self, stats, endpoint, chunk_size, compat):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.stats = stats
        self.endpoint = endpoint
        self.chunk_size = chunk_size
        self.compat = compat

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('WEBHOOK_ENABLED'):
            raise NotConfigured

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

        compat = (
            getattr(crawler.spider, 'webhook_compat', None) or
            crawler.settings.getbool('WEBHOOK_COMPAT', False)
        )

        return cls(crawler.stats, endpoint, chunk_size, compat)

    def open_spider(self, spider):
        self.logger.debug(
            'Started: %s',
            {
                'endpoint': self.endpoint,
                'chunk_size': self.chunk_size,
                'compat': self.compat,
            },
        )
        self.items: List[Dict] = []
        self.client = requests.Session()

    def process_item(self, item, spider):
        post = dict(item)
        if self.compat:
            post = self.adapt_schema(post)
        self.items.append(post)
        if len(self.items) >= self.chunk_size:
            self.send_items()
        return item

    def close_spider(self, spider):
        self.send_items()
        self.client.close()

    def send_items(self):
        response = self.client.post(self.endpoint, json=self.items)
        self.stats.inc_value('webhook/items_count', len(self.items))
        if response.ok:
            self.stats.inc_value('webhook/response_count')
        self.stats.inc_value(f'webhook/response_status_count/{response.status_code}')
        self.items.clear()

    @staticmethod
    def adapt_schema(post: Dict) -> Dict:
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


class ScrapyMetaFieldPipeline:
    """
    To every item assign `scrapy_project` and `scrapy_spider` fields.
    """
    def process_item(self, item, spider):
        item['scrapy_project'] = spider.settings.get('BOT_NAME')
        item['scrapy_spider'] = spider.name
        return item


class SentimentSourceFieldPipeline:
    """
    To every item assign predefined `source` field, drop on failure.
    """
    host_source_matches = {
        'apple.com': 'Itunes.apple.com',
        'apps.apple.com': 'Itunes.apple.com',
        'bet.championat.com': 'Чемпионат',
        'betonmobile.ru': 'Betonmobile',
        'bookmaker-ratings.ru': 'Рейтинг Букмекеров',
        'championat.com': 'Чемпионат',
        'kushvsporte.ru': 'Kush v sporte',
        'legalbet.ru': 'Legalbet',
        'overbetting.ru': 'overbetting',
        'sports.ru': 'Sports.ru',
        'vprognoze.ru': 'vprognoze',
        'vseprosport.ru': 'ВсеПроСпорт.ру',
    }

    def process_item(self, item, spider):
        host = urlparse(item.get('url')).netloc.replace('www.', '')
        source = self.host_source_matches.get(host)
        if source:
            item['source'] = source
            return item
        else:
            raise DropItem('source_not_found')


class ImagesPipeline(ImagesPipeline_):
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('IMAGES_ENABLED'):
            raise NotConfigured

    def file_path(self, request, response=None, info=None):
        f = furl(request.url)
        return f.host + f.pathstr
