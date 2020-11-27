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
