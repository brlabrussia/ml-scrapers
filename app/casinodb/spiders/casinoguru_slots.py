import scrapy

from casinodb.settings import CASINOGURU_CUSTOM_SETTINGS


class CasinoguruSlotsSpider(scrapy.Spider):
    name = 'casinoguru_slots'
    allowed_domains = ['casino.guru']
    custom_settings = CASINOGURU_CUSTOM_SETTINGS

    def start_requests(self):
        yield scrapy.Request(
            'https://casino.guru/free-casino-games',
            self.parse_slots_list,
            meta={'dont_cache': True},
        )

    def parse_slots_list(self, response):
        slot_items = response.css('.game-item')
        for si in slot_items:
            slot_url = si.css('[data-userscore-play-free]::attr(href)').get()
            slot_name = si.css('.game-item-content-heading::text').get().strip()
            yield scrapy.Request(
                slot_url,
                self.parse_slot,
                cb_kwargs={'slot_name': slot_name},
                meta={'dont_cache': False},
            )
        next_page = response.css('.paging-right a::attr(href)').get()
        if next_page:
            next_page = response.urljoin(next_page)
            yield response.request.replace(url=next_page)

    def parse_slot(self, response, slot_name):
        yield {
            'source': 'casinoguru',
            'type': 'slots',
            'name': slot_name,
            'url': response.url,
            'iframe_original': response.css('#game_link::attr(data-url)').get(),
            'iframe_fallback': response.css('#game_link::attr(data-fallback-url)').get(),
            'images_logo': response.css('.game-info--image img::attr(src)').get(),
            'images_content': response.css('.games-content--image::attr(src)').getall(),
            'videos': response.css('.video-wrapper iframe::attr(src)').getall(),
        }
