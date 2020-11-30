import requests
import scrapy
from scrapy.selector import Selector

from mfo.items import VsezaimyonlineLoader


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
        vl = VsezaimyonlineLoader(response=response)
        vl.add_value('scraped_from', response.url)
        vl.add_css('trademark', '.zaym-name::text')
        vl.add_css('logo_origin_url', '.logo-company::attr(src)')
        vl.add_xpath('ogrn', '//div[has-class("vab")]//li[starts-with(normalize-space(text()), "ОГРН")]/text()', re=r'\d{13}')
        vl.add_xpath('inn', '//div[has-class("vab")]//li[starts-with(normalize-space(text()), "ИНН")]/text()', re=r'\d{10}')
        decline_reasons_id = response.xpath('//*[@id="single_content_wrap"]//li[normalize-space(text())="Причины отказа"]/@data-id').get()
        if decline_reasons_id:
            vl.add_css('decline_reasons', f'#single_content_wrap .right-block div[data-id="{decline_reasons_id}"] *::text')
        socials_id = response.xpath('//*[@id="single_content_wrap"]//li[normalize-space(text())="Служба поддержки"]/@data-id').get()
        if socials_id:
            vl.add_css('socials', f'#single_content_wrap .right-block div[data-id="{socials_id}"] li a::attr(href)')
        vl.add_value('documents', documents)

        # `decision_speed` and `payment_speed` are loaded separately
        company_id = response.css('script').re_first('window.company_id = (\d+)')
        if company_id:
            url = f'https://vsezaimyonline.ru/actions/load_card_for_company?company_id={company_id}'
            r = requests.get(url)
            selector = Selector(text=r.json().get('code', ''))
            xp = '//div[starts-with(normalize-space(text()), "{}")]/div/text()'
            decision_speed = selector.xpath(xp.format('Скорость рассмотрения заявки')).get()
            payment_speed = selector.xpath(xp.format('Скорость выплаты')).get()
            vl.add_value('decision_speed', decision_speed)
            vl.add_value('payment_speed', payment_speed)

        yield vl.load_item()
