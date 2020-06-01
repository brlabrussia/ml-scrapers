import scrapy
from furl import furl
from slugify import slugify


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
            f = furl(response.request.url)
            f.args['cISO'] = country
            yield scrapy.Request(
                url=f.url,
                callback=self.parse_providers_list,
                meta={'dont_cache': True},
            )

    def parse_providers_list(self, response):
        provider_items = response.css('.providerCard')
        for ci in provider_items:
            provider_url = ci.css('.providerName::attr(href)').get()
            provider_name = ci.css('.providerName::text').get()
            if not provider_url or not provider_name:
                continue
            provider_url = furl(provider_url).pathstr
            yield scrapy.Request(
                response.urljoin(provider_url),
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
        # TODO switch to item loader
        item = {
            'source': 'slotcatalog',
            'type': 'providers',
            'name': provider_name,
            'url': response.request.url,
            'countries': response.css('.sixNameLeftCountries[data-label=Country] a::text').getall(),
        }
        attr_blocks = response.css('.provDetail') or ()
        for ab in attr_blocks:
            attr_name = ab.css('.provDetailTitle::text').get()
            if not attr_name:
                continue
            attr_name = slugify(attr_name, separator='_')
            attr_value = ab.css('.provDetailField *::text').getall()
            if attr_name == 'website':
                attr_value = ab.css('.provDetailField a::attr(href)').getall()
            item[attr_name] = attr_value
        for key in item:
            if isinstance(item[key], list):
                item[key] = ''.join(item[key]).strip()
        yield item
