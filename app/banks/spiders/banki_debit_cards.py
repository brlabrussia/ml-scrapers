import re

import bleach
import scrapy
from scrapy.loader.processors import Identity, Join, MapCompose

from banks.items import DebitCard
from default.items import DefaultLoader, format_date, normalize_space


class Loader(DefaultLoader):
    default_item_class = DebitCard

    banki_bank_url_in = MapCompose(
        DefaultLoader.default_input_processor,
        lambda x: ('https://www.banki.ru' + x) if x.startswith('/') else x,
    )
    images_in = MapCompose(
        lambda x: x if x else None,
    )
    borrower_registration_in = MapCompose(
        lambda x: x.replace('<', ' <'),
        lambda x: x.split('</li>'),
        lambda x: bleach.clean(x, tags=[], strip=True),
        DefaultLoader.default_input_processor,
    )
    borrower_registration_out = Identity()
    debit_bonuses_in = MapCompose(
        lambda x: x.replace('<', ' <'),
        lambda x: x.split('<li>'),
        lambda x: x.split('</li>'),
        lambda x: bleach.clean(x, tags=[], strip=True),
        DefaultLoader.default_input_processor,
    )
    debit_bonuses_out = Identity()
    updated_at_in = MapCompose(format_date)

    _ = \
        summary_out = \
        expert_positive_out = \
        expert_negative_out = \
        expert_restrictions_out = \
        debit_type_out = \
        technological_features_out = \
        interest_accrual_in = \
        service_cost_in = \
        foreign_cash_withdrawal_in = \
        foreign_cash_pickup_point_in = \
        operations_limit_in = \
        additional_information_out = \
        Identity()

    _ = \
        debit_cashback_description_out = \
        cash_withdrawal_out = \
        cash_pickup_point_out = \
        Join()


class Spider(scrapy.Spider):
    name = 'banki_debit_cards'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_banks)

    def parse_banks(self, response):
        pattern = r'/products/debitcards/[^/]+/'
        for link in response.css('td a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_banks)

    def parse_links(self, response):
        pattern = r'/products/debitcards/card/\d+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_items)

    def parse_items(self, response):
        loader = Loader(response=response)

        loader.add_value('banki_url', response.url)
        loader.add_css('banki_bank_url', '.stella a::attr(href)', re=r'/banks/bank/[^/]+/')

        loader.add_css('name', '.header-h0::text')
        images = {
            response.css('.js-product-title::text').get():
            response.css('.js-product-design::attr(src)').get(),
            **{
                s.css('::attr(title)').get(): s.css('::attr(data-img)').get()
                for s in response.css('.product-variants-panel li')
            },
        }
        images.pop(None, '')
        loader.add_value('images', images)
        loader.add_xpath('summary', '//*[has-class("widget__title")][normalize-space(text())="Основные характеристики"]/following-sibling::ul[@data-currency-id="RUB"]/li//text()')

        loader.add_xpath('borrower_age', self.getsel('text', 'Возраст'))
        loader.add_xpath('borrower_registration', self.getsel('node', 'Регистрация'))
        loader.add_xpath('expert_positive', self.getsel('alltext', 'Плюсы'))
        loader.add_xpath('expert_negative', self.getsel('alltext', 'Минусы'))
        loader.add_xpath('expert_restrictions', self.getsel('alltext', 'Особые ограничения'))

        loader.add_xpath('debit_type', self.getsel('list', 'Тип карты'))
        loader.add_xpath('technological_features', self.getsel('list', 'Технологические особенности'))
        loader.add_xpath('debit_cashback', self.getsel('cashback', 'Cash Back'))
        loader.add_xpath('debit_cashback_description', self.getsel('note', 'Cash Back'))
        loader.add_xpath('debit_bonuses', self.getsel('node', 'Бонусы'))
        loader.add_value('interest_accrual', self.extract_per_currency(response, 'alltext', 'Начисление процентов на остаток средств на счете'))
        loader.add_value('service_cost', self.extract_per_currency(response, 'alltext', 'Выпуск и годовое обслуживание'))
        loader.add_xpath('cash_withdrawal', self.getsel('alltext', 'Снятие наличных в банкоматах банка', 'RUB'))
        loader.add_xpath('cash_pickup_point', self.getsel('alltext', 'Снятие наличных в ПВН банка', 'RUB'))
        loader.add_value('foreign_cash_withdrawal', self.extract_per_currency(response, 'alltext', 'Снятие наличных в банкоматах других банков'))
        loader.add_value('foreign_cash_pickup_point', self.extract_per_currency(response, 'alltext', 'Снятие наличных в ПВН других банков'))
        loader.add_value('operations_limit', self.extract_per_currency(response, 'text', 'Лимиты по операциям'))
        loader.add_xpath('additional_information', self.getsel('list', 'Дополнительная информация'))
        loader.add_xpath('updated_at', self.getsel('text', 'Дата актуализации'))

        yield loader.load_item()

    def getsel(self, type_to_extract, field_name, currency=None):
        sel = (
            '//*[has-class("definition-list__item")]{}'
            '/*[has-class("definition-list__title")][starts-with(normalize-space(text()), "{}")]'
            '/following-sibling::*[has-class("definition-list__desc")][1]{}'
        )
        as_node = '/node()'
        as_text = '/text()'
        as_cashback = '/div/div/text()'
        as_alltext = '//*/text()'
        as_list = '//ul/li/text()'
        as_note = '//*[has-class("markup-inside-small")]//text()'
        return sel.format(
            f'[@data-currency-id="{currency}"]' if currency else '',
            field_name,
            locals()[f'as_{type_to_extract}'],
        )

    def extract_per_currency(self, response, type_to_extract, field_name):
        ret = {}
        for currency in ['RUB', 'USD', 'EUR']:
            vals = response.xpath(self.getsel(
                type_to_extract,
                field_name,
                currency,
            ))
            if not vals:
                continue
            if field_name.startswith('Начисление процентов на остаток'):
                ret[currency] = '; '.join([
                    normalize_space(val) for val in vals.getall()
                    if normalize_space(val)
                ])
            else:
                for val in vals:
                    val = normalize_space(val.get())
                    if val:
                        val = re.sub(r' ?(\₽|\$|\€)', '', val)  # service_cost
                        ret[currency] = val
                        break
        return ret or None
