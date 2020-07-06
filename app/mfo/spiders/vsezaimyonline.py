import scrapy
from scrapy.loader import ItemLoader

from mfo.items import VsezaimyonlineItem


class VsezaimyonlineSpider(scrapy.Spider):
    name = 'vsezaimyonline'
    allowed_domains = ['vsezaimyonline.ru']

    def start_requests(self):
        url = 'https://vsezaimyonline.ru/mfo'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        for link in response.css('.company_title::attr(href)'):
            yield response.follow(link, self.parse_info)

    def parse_info(self, response):
        documents = []
        for document_block in response.css('.documents_tab a'):
            documents.append({
                'name': document_block.css('::text').get(),
                'url': document_block.css('::attr(href)').get(),
            })
        il = ItemLoader(VsezaimyonlineItem(), response=response)
        il.add_css('subject', '.zaym-name::text')
        il.add_value('url', response.url)
        il.add_xpath('ogrn', '//div[has-class("vab")]//li[starts-with(normalize-space(text()), "ОГРН")]/text()', re=r'\d{5,}')
        il.add_xpath('inn', '//div[has-class("vab")]//li[starts-with(normalize-space(text()), "ИНН")]/text()', re=r'\d{5,}')
        il.add_css('refusal_reasons', 'div[data-id="1"] li::text')
        il.add_css('social_networks', 'div[data-id="2"] li a::attr(href)')
        il.add_value('documents', documents)
        yield il.load_item()
