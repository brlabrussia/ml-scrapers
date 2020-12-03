import json
from urllib.parse import unquote, urlparse

import scrapy
from funcy import rcompose
from scrapy.loader.processors import Identity, Join, MapCompose

from banks.items import Deposit
from default.items import DefaultLoader, drop_blank, format_date, format_url


class Loader(DefaultLoader):
    default_item_class = Deposit

    banki_bank_url_in = MapCompose(format_url)
    is_staircase_contribution_in = MapCompose(
        DefaultLoader.default_input_processor,
        str.lower,
        lambda x: True if x == 'да' else False,
    )
    replenishment_ability_in = MapCompose(
        DefaultLoader.default_input_processor,
        str.lower,
        rcompose(
            r'^(нет$|возможно$|возможно, но)',
            {'нет': 0, 'возможно': 1, 'возможно, но': 2, None: None},
        ),
    )
    rates_comments_in = MapCompose(
        str.splitlines,
        lambda x: x.lstrip('* '),
        drop_blank,
    )
    auto_prolongation_in = MapCompose(
        DefaultLoader.default_input_processor,
        str.lower,
        rcompose(
            r'^(невозможна|возможна)$',
            {'невозможна': 0, 'возможна': 1, None: None},
        ),
    )
    updated_at_in = MapCompose(format_date)

    _ = \
        special_conditions_out = \
        rates_table_in = \
        rates_comments_out = \
        Identity()

    _ = \
        deposit_amount_out = \
        deposit_term_out = \
        capitalization_out = \
        replenishment_description_out = \
        partial_withdrawal_description_out = \
        Join()


class Spider(scrapy.Spider):
    name = 'banki_deposits'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_banks)

    def parse_banks(self, response):
        pattern = r'/products/deposits/[^/]+/'
        for link in response.css('td a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)
            yield response.follow(
                link.replace('/deposits/', '/credits/'),
                self.parse_cities,
            )
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_banks)

    def parse_cities(self, response):
        pattern = urlparse(response.url).path + r'(?!calculator)[^/]+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(
                link.replace('/credits/', '/deposits/'),
                self.parse_links,
            )

    def parse_links(self, response):
        pattern = r'/products/deposits/deposit/\d+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_items)

    def parse_items(self, response):
        loader = Loader(response=response)
        loader.add_value('banki_url', response.url)
        loader.add_xpath('banki_bank_url', '//h1/ancestor::header/following-sibling::div//a/@href')
        loader.add_css('name_base', '.bread-crumbs__item:last-child *::text')
        loader.add_css('name_full', '[data-test=deposit-header-title]::text')

        try:
            module_options = response.css('[data-module*=DepositsBundle]::attr(data-module-options)').get()
            module_options_obj = json.loads(unquote(module_options))

            rates_obj = module_options_obj['ratesByCurrency']
            rates_obj_cur = next(iter(rates_obj.items()))[1]
            loader.add_value('deposit_amount', f'от {rates_obj_cur["amountFrom"]}')
            loader.add_value('deposit_amount', f'до {rates_obj_cur["amountTo"]}' if rates_obj_cur['amountTo'] else None)
            loader.add_value('deposit_currency', rates_obj_cur['symbol'])
            loader.add_value('deposit_term', 'от' if not rates_obj_cur['periodOne'] else None)
            loader.add_value('deposit_term', str(rates_obj_cur['periodFrom']))

            loader.add_value('rates_table', module_options_obj['rateTable'])
            loader.add_value('rates_comments', module_options_obj['productData'].get('rate_comment'))
        except Exception:
            self.logger.info(f'Cannot process rates module options for: {response.url}')
            return

        sel = (
            '//*[has-class("deposit-info-params-item")]'
            '/dt[normalize-space(text())="{}"]'
            '/../dd{}'
        )
        as_text = '//text()'
        as_list = '//ul/li/text()'
        as_note = '//div//text()'
        loader.add_xpath('interest_payment', sel.format('Выплата процентов', as_text))
        loader.add_xpath('interest_payment_description', sel.format('Выплата процентов', as_note))
        loader.add_xpath('capitalization', sel.format('Капитализация', as_text))
        loader.add_xpath('special_contribution', sel.format('Специальный вклад', as_text))
        loader.add_xpath('special_contribution_description', sel.format('Специальный вклад', as_note))
        loader.add_xpath('is_staircase_contribution', sel.format('Лестничный вклад', as_text))
        loader.add_xpath('special_conditions', sel.format('Особые условия', as_list))
        loader.add_xpath('replenishment_ability', sel.format('Пополнение', as_text))
        loader.add_xpath('replenishment_description', sel.format('Пополнение', f'//*{as_text}'))
        loader.add_xpath('min_irreducible_balance', sel.format('Минимальный неснижаемый остаток', as_text))
        loader.add_xpath('early_dissolution', sel.format('Досрочное расторжение', as_text))
        loader.add_xpath('early_dissolution_description', sel.format('Досрочное расторжение', as_note))
        loader.add_xpath('auto_prolongation', sel.format('Автопролонгация', as_text))
        loader.add_xpath('auto_prolongation_description', sel.format('Автопролонгация', as_note))
        loader.add_xpath('partial_withdrawal', sel.format('Частичное снятие', as_text))
        loader.add_xpath('partial_withdrawal_description', sel.format('Частичное снятие', f'//*{as_text}'))
        loader.add_xpath('online_opening', sel.format('Открытие вклада online', as_text))
        loader.add_css('updated_at', '.expand-content span::text', re=r'Дата актуализации: (.+)\.\s')

        yield loader.load_item()
