import scrapy

from mfo.items import ZaymovLoader


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
        xp = '//*[has-class("sec")][normalize-space(text())="{}"]/../*[has-class("the")]/text()'
        zl = ZaymovLoader(response=response)
        zl.add_value('scraped_from', response.url)
        zl.add_css('trademark', 'article h1::text')
        zl.add_css('logo_origin_url', '.mfologo img::attr(src)')
        zl.add_xpath('cbrn', xp.format('лицензия №'), re=r'\d{13}$')
        zl.add_xpath('ogrn', xp.format('ОГРН'), re=r'\d{13}$')
        zl.add_xpath('cbr_created_at', xp.format('дата внесения в реестр'))
        zl.add_xpath('address', xp.format('адрес'))
        zl.add_xpath('website', xp.format('официальный сайт'))
        yield zl.load_item()
