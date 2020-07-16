import scrapy


class ZaymovSpider(scrapy.Spider):
    name = 'zaymov'
    allowed_domains = ['zaymov.net']

    def start_requests(self):
        url = 'https://zaymov.net/mfo'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        for link in response.css('.mfologo .more::attr(href)'):
            yield response.follow(link, self.parse_info)
        next_page = response.css('.eshe a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_subjects)

    def parse_info(self, response):
        item = {
            'subject': response.css('article h1::text').get(),
            'url': response.url,
            'logo': response.css('.mfologo img::attr(src)').get(),
            'props': {},
        }
        prop_blocks = response.css('.fir')
        for pb in prop_blocks:
            prop_name = pb.css('.sec::text').get()
            prop_value_block = pb.css('.the')
            prop_value = {
                'text': prop_value_block.css('::text').get(),
                'data-link': prop_value_block.css('::attr(data-link)').get(),
            }
            item['props'][prop_name] = prop_value
        yield item
