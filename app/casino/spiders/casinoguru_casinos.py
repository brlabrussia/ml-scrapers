import scrapy

from casino.settings import CASINOGURU_CUSTOM_SETTINGS


class CasinoguruCasinosSpider(scrapy.Spider):
    name = 'casinoguru_casinos'
    allowed_domains = ['casino.guru']
    custom_settings = CASINOGURU_CUSTOM_SETTINGS

    def start_requests(self):
        yield scrapy.Request(
            'https://casino.guru/top-online-casinos',
            self.parse_casinos_list,
            cookies={'casinoTab': 'ALL'},
            meta={'dont_cache': True},
        )

    def parse_casinos_list(self, response):
        casino_items = response.css('.casino-card')
        for ci in casino_items:
            yield {
                'source': 'casinoguru',
                'type': 'casinos',
                'name': ci.css('.casino-hard-header-name .text-bold a::text').get(),
                'url': ci.css('.casino-hard-header-name a::attr(href)').get(),
                'images_logo': ci.css('.casino-card-logo img::attr(src)').get(),
            }
        next_page = response.css('.paging-right a::attr(href)').get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield response.request.replace(url=next_page)
