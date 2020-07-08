from scrapy.extensions.httpcache import DummyPolicy


class CasinoguruCachePolicy(DummyPolicy):
    def should_cache_response(self, response, request):
        return response.status == 200
