import json

import scrapy
from furl import furl


class SlotcatalogSlotsSpider(scrapy.Spider):
    name = 'slotcatalog_slots'
    allowed_domains = ['slotcatalog.com']

    def start_requests(self):
        url = 'https://slotcatalog.com/en/The-Best-Slots'
        yield scrapy.Request(
            furl(url).set({'cISO': 'RU'}).url,
            self.parse_slots_list,
            meta={'dont_cache': True},
        )

    def parse_slots_list(self, response):
        slot_items = response.css('.providerCard')
        for si in slot_items:
            slot_url = si.css('.providerName::attr(href)').get()
            slot_name = si.css('.providerName::text').get()
            if not slot_url or not slot_name:
                continue
            yield response.follow(
                furl(slot_url).set({'cISO': 'RU'}).url,
                self.parse_slot,
                cb_kwargs={'slot_name': slot_name},
                meta={'dont_cache': False},
            )
        next_page = response.css('.navpag-cont .active + li a::attr(p)').get()
        if next_page:
            url = furl(response.url).set({'cISO': 'RU', 'p': next_page}).url
            yield response.request.replace(url=url)

    def parse_slot(self, response, slot_name):
        def extract_props(css_prop_blocks, css_prop_name, css_prop_value):
            props = {}
            prop_blocks = response.css(css_prop_blocks)
            for pb in prop_blocks:
                prop_name = pb.css(css_prop_name).get()
                if not prop_name:
                    continue
                prop_value = pb.css(css_prop_value).getall()
                props[prop_name.strip()] = ''.join(prop_value).strip()
            return props
        item = {
            'source': 'slotcatalog',
            'type': 'slots',
            'name': slot_name,
            'url': furl(response.url).set({}).url,
            'props_upper': extract_props('.slot_page_item_one > div', 'p::text', 'span *::text'),
            'props_lower': extract_props('.slotAttrTable tr', '.propLeft::text', '.propRight *::text'),
            'tags': response.css('.tegs_slot_item a::text').getall(),
            'json': json.loads(response.css('#divSlotPage script[type$=json]::text').get() or '{}'),
        }
        slug = furl(response.url).path.segments[-1]
        query = {
            'slottranslit': slug,
            'ajax': 1,
            'blck': 'gameContainer',
        }
        url = furl('https://slotcatalog.com/index.php', query=query).url
        yield scrapy.Request(url, self.parse_iframe, cb_kwargs={'item': item})

    def parse_iframe(self, response, item):
        item.update({
            'iframe_original': response.css('.iframeGame::attr(src)').get(),
            'iframe_fallback': item.get('url').replace('slots', 'play'),
        })
        yield item
