from http import HTTPStatus

from default.settings import *

BOT_NAME = 'casinodb'
SPIDER_MODULES = ['casinodb.spiders']
NEWSPIDER_MODULE = 'casinodb.spiders'

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [hs.value for hs in HTTPStatus if hs.value != 200]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.DbmCacheStorage'

PROXY_PROVIDER = 'nordvpn'  # TODO switch to `NORDVPN_ENABLED = True`
