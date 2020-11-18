import re

import scrapy

from banks.items import BankiCreditCardLoader, normalize_spaces


class BankiCreditCardsSpider(scrapy.Spider):
    name = 'banki_credit_cards'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_banks)

    def parse_banks(self, response):
        pattern = r'/products/creditcards/[^/]+/'
        for link in response.css('td a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_banks)

    def parse_links(self, response):
        pattern = r'/products/creditcards/card/\d+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_items)

    def parse_items(self, response):
        loader = BankiCreditCardLoader(response=response)

        loader.add_value('banki_url', response.url)
        loader.add_css('banki_bank_url', '.stella a::attr(href)', re=r'/banks/bank/[^/]+/')

        loader.add_xpath('credit_type', self.getsel('list', 'Тип карты'))
        loader.add_xpath('technological_features', self.getsel('list', 'Технологические особенности'))
        loader.add_xpath('credit_cashback', self.getsel('alltext', 'Cash Back'))
        loader.add_xpath('credit_bonuses', self.getsel('alltext', 'Бонусы'))
        loader.add_xpath('interest_accrual', self.getsel('alltext', 'Начисление процентов на остаток средств на счете'))
        loader.add_value('service_cost', self.extract_per_currency(response, 'alltext', 'Выпуск и годовое обслуживание'))
        loader.add_xpath('cash_withdrawal', self.getsel('alltext', 'Снятие наличных в банкоматах банка', 'RUB'), re=r'(\d+)\%')
        loader.add_xpath('cash_pickup_point', self.getsel('alltext', 'Снятие наличных в ПВН банка', 'RUB'), re=r'([\d,]+)\%')
        loader.add_value('foreign_cash_withdrawal', self.extract_per_currency(response, 'alltext', 'Снятие наличных в банкоматах других банков'))
        loader.add_value('foreign_cash_pickup_point', self.extract_per_currency(response, 'alltext', 'Снятие наличных в ПВН других банков'))
        loader.add_value('operations_limit', self.extract_per_currency(response, 'text', 'Лимиты по операциям'))
        loader.add_xpath('additional_information', self.getsel('list', 'Дополнительная информация'))
        loader.add_xpath('updated_at', self.getsel('text', 'Дата актуализации'))

        loader.add_xpath('own_funds', self.getsel('text', 'Использование собственных средств'))

        yield loader.load_item()

    def getsel(self, type_to_extract, field_name, currency=None):
        sel = (
            '//*[has-class("definition-list__item")]{}'
            '/*[has-class("definition-list__title")][starts-with(normalize-space(text()), "{}")]'
            '/following-sibling::*[has-class("definition-list__desc")][1]{}'
        )
        as_node = '/node()'
        as_text = '/text()'
        as_alltext = '//*/text()'
        as_list = '//ul/li/text()'
        as_note = '/*[has-class("text-note")]/p/text()'
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
            for val in vals:
                val = normalize_spaces(val.get())
                if val:
                    val = re.sub(r' ?(\₽|\$|\€)', '', val)  # service_cost
                    ret[currency] = val
                    break
            {
                'currency': currency,
                'currency_service_cost': val,
            }
        return ret
