import scrapy

from banks.items import BankiBankLoader


class BankiBanksSpider(scrapy.Spider):
    name = 'banki_banks'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        pattern = r'/banks/bank/[^/]+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_bank)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_links)

    def parse_bank(self, response):
        bbl = BankiBankLoader(response=response)
        bbl.add_value('banki_url', response.url)
        bbl.add_css('name', '[data-test=bankpage-header-bankname]::text')
        bbl.add_css('reg_number', '[data-test=bankpage-header-banklicense]::text', re=r'(\d+(-\w+)?)')
        bbl.add_css('ogrn', '[data-test=bankpage-header-ogrn]::text', re=r'\d{5,}')
        yield bbl.load_item()
