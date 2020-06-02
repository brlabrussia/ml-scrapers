import json
import logging
import random

import requests
from scrapy.exceptions import CloseSpider, NotConfigured
from w3lib.http import basic_auth_header


class NordVPNProxyMiddleware:
    def __init__(self, creds):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.proxy = self.get_proxy()
        self.proxy_auth = basic_auth_header(*creds)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('NORDVPN_ENABLED'):
            raise NotConfigured

        if crawler.settings.getint('CONCURRENT_REQUESTS') != 1:
            raise CloseSpider('multiple_concurrent_requests')

        creds = (
            crawler.settings.get('NORDVPN_USERNAME'),
            crawler.settings.get('NORDVPN_PASSWORD'),
        )
        if not all(creds):
            raise CloseSpider('credentials_not_set')

        return cls(creds)

    def open_spider(self, spider):
        self.logger.debug(f'Using `{self.proxy}` as proxy')

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            return
        request.meta['proxy'] = self.proxy
        request.headers['Proxy-Authorization'] = self.proxy_auth

    def get_proxy(self) -> str:
        """
        Get proxy for current session randomly chosen from list of NordVPN servers
        currently online and supporting proxy_ssl.

        We query multiple and only choose one for situations where this one
        proxy can have temporary issues resulting in middleware not working.

        TODO allow specifying prefered countries in project settings
        """
        filters = {
            'country_id': 208,  # Sweden
            'servers_technologies': [21],  # proxy_ssl
        }
        response = requests.get(
            'https://nordvpn.com/wp-admin/admin-ajax.php',
            params={
                'action': 'servers_recommendations',
                # use `json.dumps()` manually to set `separators` without space (colon)
                'filters': json.dumps(filters, separators=(',', ':')),
                'limit': 4,
            },
        )
        hostnames = [
            server.get('hostname')
            for server in response.json()
            if server.get('hostname')
        ]
        return random.choice(hostnames)
