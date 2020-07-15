import scrapy


class BankiSpider(scrapy.Spider):
    name = 'banki'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        # url = 'https://www.banki.ru/microloans/companies/'
        # yield scrapy.Request(url, callback=self.parse_subjects)
        for i in range(1, 400):
            url = f'https://www.banki.ru/microloans/products/{i}/'
            yield scrapy.Request(url, callback=self.parse_product)

    def parse_subjects(self, response):
        css = '*[data-test=mfo-item-company]::attr(href)'
        for link in response.css(css):
            yield response.follow(link, self.parse_subject)

    def parse_subject(self, response):
        css = '*[data-test=mfo-widget] tbody tr td:first-child a::attr(href)'
        for link in response.css(css).getall():
            yield response.follow(link, self.parse_product)

    def parse_product(self, response):
        item = {
            'subject': response.css('h1::text').get(),
            'url': response.url,
            'logo': response.css('[data-test=mfo-logo]::attr(src)').get(),
            'actualization': response.xpath('//*[has-class("text-note")][starts-with(normalize-space(text()), "Дата актуализации")]/text()').get(),
            'props': {},
        }
        prop_blocks = response.css('.definition-list__item')
        for pb in prop_blocks:
            prop_name = pb.css('.definition-list__key::text').get()
            prop_value_block = pb.css('.definition-list__value')
            prop_value = {
                'text': prop_value_block.css('::text').get(),
                'note': prop_value_block.css('.text-note p::text').get(),
                'list': prop_value_block.css('li::text').getall(),
                'links': [
                    {
                        'text': link.css('::text').get(),
                        'href': link.css('::attr(href)').get(),
                    }
                    for link in prop_value_block.css('a')
                ],
            }
            item['props'][prop_name] = prop_value
        yield item
