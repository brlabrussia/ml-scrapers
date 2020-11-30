import scrapy
from furl import furl


class SlotcatalogCasinosSpider(scrapy.Spider):
    name = 'slotcatalog_casinos'
    allowed_domains = ['slotcatalog.com']

    def start_requests(self):
        yield scrapy.Request(
            'https://slotcatalog.com/en/Top-Online-Casinos',
            self.parse_countries,
            meta={'dont_cache': True},
        )

    def parse_countries(self, response):
        countries = response.css('select[name=cISO] option::attr(value)').getall()
        for country in countries:
            yield scrapy.Request(
                furl(response.url).set({'cISO': country}).url,
                self.parse_casinos_list,
                meta={'dont_cache': True},
            )

    def parse_casinos_list(self, response):
        casino_items = response.css('.providerCard')
        for ci in casino_items:
            casino_url = ci.css('.providerName::attr(href)').get()
            casino_name = ci.css('.providerName::text').get()
            if not casino_url or not casino_name:
                continue
            yield scrapy.Request(
                furl(response.url).join(casino_url).set({'cISO': 'RU'}).url,
                self.parse_casino,
                cb_kwargs={'casino_name': casino_name},
                meta={'dont_cache': False},
            )
        next_page = response.css('.navpag-cont .active + li a::attr(p)').get()
        if next_page:
            f = furl(response.request.url)
            f.args['p'] = next_page
            yield response.request.replace(url=f.url)

    def parse_casino(self, response, casino_name):
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
        yield {
            'source': 'slotcatalog',
            'type': 'casinos',
            'name': casino_name,
            'url': furl(response.url).set({}).url,
            'props_upper': extract_props('.casino_prop_item_pad', '.prop_name::text', '.prop_number::text'),
            'props_lower': extract_props('.detail-tab', '.detail-tab-title::text', '.detail-tab-field *::text'),
            'countries': response.css('.CasinoNameLeftCountries[data-label=Countries] a:last-child::text').getall(),
            'providers': response.css('.CasinoNameLeft[data-label="Provider Name"] a::attr(href)').getall(),
        }
