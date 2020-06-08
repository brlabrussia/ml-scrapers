import scrapy
from furl import furl


class SlotcatalogProvidersSpider(scrapy.Spider):
    name = 'slotcatalog_providers'
    allowed_domains = ['slotcatalog.com']

    def start_requests(self):
        yield scrapy.Request(
            'https://slotcatalog.com/en/Providers',
            self.parse_countries,
            meta={'dont_cache': True},
        )

    def parse_countries(self, response):
        countries = response.css('select[name=cISO] option::attr(value)').getall()
        for country in countries:
            yield scrapy.Request(
                furl(response.url).set({'cISO': country}).url,
                self.parse_providers_list,
                meta={'dont_cache': True},
            )

    def parse_providers_list(self, response):
        provider_items = response.css('.providerCard')
        for ci in provider_items:
            provider_url = ci.css('.providerName::attr(href)').get()
            provider_name = ci.css('.providerName::text').get()
            if not provider_url or not provider_name:
                continue
            yield scrapy.Request(
                furl(response.url).join(provider_url).set({'cISO': 'RU'}).url,
                self.parse_provider,
                cb_kwargs={'provider_name': provider_name},
                meta={'dont_cache': False},
            )
        next_page = response.css('.navpag-cont .active + li a::attr(p)').get()
        if next_page:
            f = furl(response.request.url)
            f.args['p'] = next_page
            yield response.request.replace(url=f.url)

    def parse_provider(self, response, provider_name):
        def extract_props(css_prop_blocks, css_prop_name, css_prop_value):
            props = {}
            prop_blocks = response.css(css_prop_blocks)
            for pb in prop_blocks:
                prop_name = pb.css(css_prop_name).get()
                if not prop_name:
                    continue
                if prop_name.strip().lower().startswith('website'):
                    css_prop_value_website = css_prop_value.replace('*::text', 'a::attr(href)')
                    prop_value = pb.css(css_prop_value_website).getall()
                else:
                    prop_value = pb.css(css_prop_value).getall()
                props[prop_name.strip()] = ''.join(prop_value).strip()
            return props
        yield {
            'source': 'slotcatalog',
            'type': 'providers',
            'name': provider_name,
            'url': furl(response.url).set({}).url,
            'props_upper': extract_props('.provider_prop_item_pad', '.prop_name::text', '.prop_number::text'),
            'props_lower': extract_props('.provDetail', '.provDetailTitle::text', '.provDetailField *::text'),
            'countries': response.css('.sixNameLeftCountries[data-label=Country] .linkOneLine::text').getall(),
        }
