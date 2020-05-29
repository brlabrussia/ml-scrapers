import json
import logging
import os
import random

import requests
from scrapy.exceptions import CloseSpider, NotConfigured
from w3lib.http import basic_auth_header


class NordVPNProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        if not crawler.settings.get('PROXY_PROVIDER', '').lower() == 'nordvpn':
            raise NotConfigured
        if crawler.settings.getint('CONCURRENT_REQUESTS') != 1:
            self.logger.error("Can't use NordVPN with `CONCURRENT_REQUESTS != 1`")
            raise CloseSpider('multiple_concurrent_requests')
        self.proxy = self.get_proxy()
        self.logger.debug(f'Using `{self.proxy}` as proxy')
        self.proxy_authorization = self.get_proxy_authorization()

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            return
        request.meta['proxy'] = self.proxy
        request.headers['Proxy-Authorization'] = self.proxy_authorization

    def get_proxy(self) -> str:
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

    def get_proxy_authorization(self) -> str:
        credentials = (os.getenv('NORDVPN_USERNAME'), os.getenv('NORDVPN_PASSWORD'))
        if not all(credentials):
            self.logger.error("Can't get credentials from `NORDVPN_USERNAME` and `NORDVPN_PASSWORD` env variables")
            raise CloseSpider('credentials_not_set')
        return basic_auth_header(*credentials)
