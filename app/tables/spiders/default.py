"""
import json
import requests
AUTH = ('user', 'pass')
PROJECT = 'tables'
SPIDER = 'test'
ARGS = [
    1234,
    'https://bsrussia.com/ratings/mirovoy-reyting',
    'smth1',
    'smth2'
]
requests.post(
    'https://scrapy.localhost/schedule.json',
    data=[('project', PROJECT), ('spider', SPIDER), ('request_args', json.dumps(ARGS))],
    verify=False,
    auth=AUTH,
)
"""

import json

import scrapy


class DefaultSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'request_args', None):
            instance_id, url, *args = json.loads(self.request_args)
            self.instance_id = instance_id
            self.start_urls = [url]
            self.args = args
