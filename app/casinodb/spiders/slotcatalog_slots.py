import scrapy
from furl import furl
from slugify import slugify


class SlotcatalogSlotsSpider(scrapy.Spider):
    name = 'slotcatalog_slots'
    allowed_domains = ['slotcatalog.com']

    def start_requests(self):
        yield scrapy.Request(
            'https://slotcatalog.com/en/The-Best-Slots',
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
                slot_url,
                self.parse_slot,
                cb_kwargs={'slot_name': slot_name},
                meta={'dont_cache': False},
            )
        next_page = response.css('.navpag-cont .active + li a::attr(p)').get()
        if next_page:
            f = furl(response.request.url)
            f.args['p'] = next_page
            yield response.request.replace(url=f.url)

    def parse_slot(self, response, slot_name):
        # TODO switch to item loader
        item = {
            'source': 'slotcatalog',
            'type': 'slots',
            'name': slot_name,
            'url': response.request.url,
            'tags': response.css('.tegs_slot_item a::text').getall(),
            'provider_url': response.css('.provider_item a::attr(href)').getall(),
            'layout': response.css('.layout_val::text').getall(),
        }
        attr_blocks = response.css('.slotAttrTable tr') or ()
        for ab in attr_blocks:
            attr_name = ab.css('.propLeft::text').get()
            if not attr_name:
                continue
            attr_name = slugify(attr_name, separator='_')
            attr_value = ab.css('.propRight *::text').getall()
            item[attr_name] = attr_value
        for key in item:
            if isinstance(item[key], list):
                sep = '' if key != 'tags' else ', '
                item[key] = sep.join(item[key]).strip()
        yield item
