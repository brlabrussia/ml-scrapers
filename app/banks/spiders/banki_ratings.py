import scrapy
from banks.items import Rating
from default.items import DefaultLoader
from default.utils import format_url
from scrapy.loader.processors import MapCompose


class Loader(DefaultLoader):
    default_item_class = Rating
    default_input_processor = MapCompose(
        lambda x: x.replace(' ', ''),
        lambda x: x.replace('−', '-'),
        int,
        lambda x: x if x != 0 else None,
    )

    _ = \
        banki_url_in = \
        banki_bank_url_in = \
        MapCompose(
            DefaultLoader.default_input_processor,
            format_url,
        )


class Spider(scrapy.Spider):
    name = 'banki_ratings'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        pattern = r'/banks/bank/[^/]+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_id)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_links)

    def parse_id(self, response):
        bank_id = response.css('script').re_first(r"var currentBankId = '(\d+?)';")
        if not bank_id:
            return
        url = f'https://www.banki.ru/banks/ratings/?BANK_ID={bank_id}'
        yield response.follow(
            url,
            self.parse_items,
            cb_kwargs={'banki_bank_url': response.url},
        )

    def parse_items(self, response, banki_bank_url):
        loader = Loader(response=response)
        loader.add_value('banki_url', response.url)
        loader.add_value('banki_bank_url', banki_bank_url)
        xp = '//td[text()="{}"]/following-sibling::td[1]/text()'
        loader.add_xpath('net_assets', xp.format('Активы нетто'))
        loader.add_xpath('net_profit', xp.format('Чистая прибыль'))
        loader.add_xpath('equity', xp.format('Капитал (по форме 123)'))
        loader.add_xpath('credit_portfolio', xp.format('Кредитный портфель'))
        loader.add_xpath('npls', xp.format('Просроченная задолженность в кредитном портфеле'))
        loader.add_xpath('private_deposits', xp.format('Вклады физических лиц'))
        loader.add_xpath('investment_in_securities', xp.format('Вложения в ценные бумаги'))
        item = loader.load_item()
        if len(item.items()) > 2:
            yield item
