import json
from html import unescape

import scrapy
from banks.items import Branch
from default.items import DefaultLoader
from default.utils import format_url, normalize_space
from scrapy.loader.processors import Compose, Identity, Join, MapCompose


class Loader(DefaultLoader):
    default_item_class = Branch
    name_in = MapCompose(unescape)
    bank_url_in = MapCompose(format_url)
    metro_out = Compose(
        Join(),
        str.strip,
    )
    schedule_in = schedule_out = Identity()


class Spider(scrapy.Spider):
    name = 'banki_branches'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        pattern = r'/banks/bank/[^/]+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_cities)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_links)

    def parse_cities(self, response):
        bank_id = response.css('script').re_first(r"var currentBankId = '(\d+?)';")
        if not bank_id:
            return
        url = f'https://www.banki.ru/bitrix/components/banks/universal.select.region/ajax.php?bankid={bank_id}&type=city'
        yield response.follow(url, self.parse_bank)

    def parse_bank(self, response):
        response_json = json.loads(response.text)
        for item in response_json['data']:
            yield response.follow(
                item['url'] + 'all',
                self.parse_items,
                cb_kwargs={
                    'region_name': item['region_name'],
                    'region_name_full': item['region_name_full'],
                },
            )

    def parse_items(self, response, region_name, region_name_full):
        for branch_elem in response.css('.list__main .list__item:not(.list__item--header)'):
            loader = Loader(response=response, selector=branch_elem)
            loader.add_css('banki_id', '::attr(data-id)')
            loader.add_css('latitude', '::attr(data-latitude)')
            loader.add_css('longitude', '::attr(data-longitude)')
            loader.add_css('name', '::attr(data-name)')
            loader.add_css('address', '::attr(data-address)')
            loader.add_css('type', '::attr(data-type)')
            loader.add_css('bank_url', '.item__name__bank::attr(href)')
            loader.add_css('bank_name', '.item__name__bank::text')
            loader.add_css('metro', '.item__location::text')
            loader.add_css('phone', '.item__location__phone::text')
            loader.add_value('region_name', region_name)
            loader.add_value('region_name_full', region_name_full)
            loader.add_value('schedule', self.extract_schedule(branch_elem))
            yield loader.load_item()
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_items)

    @staticmethod
    def extract_schedule(branch_elem):
        ret = []
        schedule_group_elems = branch_elem.css('.item__schedule__group')
        if not schedule_group_elems:
            return ret
        for schedule_group_elem in schedule_group_elems:
            ret.append({
                'title': normalize_space(schedule_group_elem.css('.item__schedule__group__title::text').get() or ''),
                'content': normalize_space(schedule_group_elem.css('.item__schedule__group__content::text').get() or ''),
            })
        return ret
