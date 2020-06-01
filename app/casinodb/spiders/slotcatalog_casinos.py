import scrapy
from furl import furl
from slugify import slugify


class SlotcatalogCasinosSpider(scrapy.Spider):
    name = 'slotcatalog_casinos'
    allowed_domains = ['slotcatalog.com']
    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
    }

    def start_requests(self):
        yield scrapy.Request(
            'https://slotcatalog.com/en/Top-Online-Casinos',
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
                callback=self.parse_casinos_list,
                meta={'dont_cache': True},
            )

    def parse_casinos_list(self, response):
        casino_items = response.css('.providerCard')
        for ci in casino_items:
            casino_url = ci.css('.providerName::attr(href)').get()
            casino_name = ci.css('.providerName::text').get()
            if not casino_url or not casino_name:
                continue
            casino_url = furl(casino_url).pathstr
            yield scrapy.Request(
                response.urljoin(casino_url),
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
        # TODO switch to item loader
        item = {
            'source': 'slotcatalog',
            'type': 'casinos',
            'name': casino_name,
            'url': response.request.url,
            'countries': response.css('.CasinoNameLeftCountries[data-label=Countries] a::text').getall(),
            'providers': response.css('.CasinoNameLeft[data-label="Provider Name"] a::attr(href)').getall(),
        }
        attr_blocks = response.css('.detail-tab') or ()
        for ab in attr_blocks:
            attr_name = ab.css('.detail-tab-title::text').get()
            if not attr_name:
                continue
            attr_name = slugify(attr_name, separator='_')
            attr_value = ab.css('.detail-tab-field *::text').getall()
            item[attr_name] = attr_value
        for key in item:
            if isinstance(item[key], list):
                item[key] = ''.join(item[key]).strip()
        yield item
