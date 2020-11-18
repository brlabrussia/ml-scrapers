from urllib.parse import urlparse

import scrapy

from banks.items import ConsumerCreditLoader
from tables.items import TableDataLoader, TableLoader


class BankiConsumerCreditsSpider(scrapy.Spider):
    name = 'banki_consumer_credits'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_banks)

    def parse_banks(self, response):
        pattern = r'/products/credits/[^/]+/'
        for link in response.css('td a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_banks)

    def parse_links(self, response):
        pattern = r'/products/credits/credit/\d+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_items)
        pattern = urlparse(response.url).path + r'[^/]+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)

    def parse_items(self, response):
        sel = (
            '//*[has-class("definition-list__key")][normalize-space(text())="{}"]'
            '/../*[has-class("definition-list__value")]{}'
        )
        as_text = '//text()'
        as_list = '//ul/li/text()'
        as_sublist = '/*[normalize-space(text())="{}"]/following-sibling::ul[1]/li/text()'
        as_note = '//*[has-class("text-note")]/text()'

        loader = ConsumerCreditLoader(response=response)
        loader.add_value('banki_url', response.url)
        loader.add_xpath('banki_bank_url', '//h1/ancestor::header/following-sibling::div//a/@href')
        loader.add_xpath('account_currency', sel.format('Валюта счета', as_text))
        loader.add_xpath('loan_purpose', sel.format('Цель кредита', as_list))
        loader.add_xpath('loan_purpose_description', sel.format('Цель кредита', as_note))
        loader.add_xpath('is_subjected_to_fee', sel.format('Комиссии', as_text))
        loader.add_xpath('loan_security', sel.format('Обеспечение', '/div/div[not(@class)]/text()'))
        loader.add_xpath('credit_insurance', sel.format('Страхование', as_list))
        loader.add_xpath('credit_insurance_description', sel.format('Страхование', as_note))
        loader.add_xpath('additional_information', sel.format('Дополнительная информация', as_text))
        loader.add_value('rates_table', self.extract_rates_table(response))
        loader.add_xpath('borrowers_category', sel.format('Категория заемщиков', as_list))
        loader.add_xpath('borrowers_age_men', sel.format('Возраст заемщика', as_sublist.format('для мужчин')))
        loader.add_xpath('borrowers_age_women', sel.format('Возраст заемщика', as_sublist.format('для женщин')))
        loader.add_xpath('work_experience', sel.format('Стаж работы', as_list))
        loader.add_xpath('borrowers_registration', sel.format('Регистрация', as_list))
        loader.add_xpath('borrowers_income_description', sel.format('Доход', as_text))
        loader.add_xpath('borrowers_income_tip', sel.format('Доход', as_note))
        loader.add_xpath('borrowers_income_documents', sel.format('Доход', as_list))
        loader.add_xpath('borrowers_documents', sel.format('Документы', as_list))
        loader.add_xpath('application_consider_time', sel.format('Срок рассмотрения заявки', as_text))
        loader.add_xpath('application_consider_time_description', sel.format('Срок рассмотрения заявки', as_note))
        loader.add_xpath('credit_decision_time', sel.format('Максимальный срок действия кредитного решения', as_text))
        loader.add_xpath('loan_processing_terms', sel.format('Оформление кредита', as_list))
        loader.add_xpath('loan_delivery_type', sel.format('Форма выдачи', as_list))
        loader.add_xpath('repayment_procedure', sel.format('Порядок погашения', as_list))
        loader.add_xpath('early_repayment_full', sel.format('Досрочное погашение', as_sublist.format('полное')))
        loader.add_xpath('early_repayment_partial', sel.format('Досрочное погашение', as_sublist.format('частичное')))
        loader.add_xpath('obligations_violation', sel.format('Нарушение обязательств по кредиту', as_text))
        loader.add_xpath('payment_method', sel.format('Способ оплаты', as_list))
        loader.add_css('updated_at', '[data-test=read-more]', re=r'Дата актуализации: (.+)\. ')

        yield loader.load_item()

    def extract_rates_table(self, response):
        tl = TableLoader(response=response)
        table_name = 'Таблица ставок'
        table_sel = response.xpath(
            f'//*[has-class("accordion__title")][normalize-space(text())="{table_name}"]'
            '/ancestor::*[has-class("accordion__item")]'
            '//*[has-class("accordion__body")]'
            '//table',
        )

        # head
        for row_sel in table_sel.css('.basic-table__row--header'):
            row_loaders = []
            for data_sel in row_sel.css('th'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.add_xpath('value', '.')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('head', [row_loaders])

        # body
        for row_sel in table_sel.css('.basic-table__row:not(.basic-table__row--header)'):
            row_loaders = []
            for data_sel in row_sel.css('td'):
                tdl = TableDataLoader(selector=data_sel)
                tdl.add_xpath('value', '.')
                tdl.add_value('value', '')
                tdl.add_xpath('colspan', './@colspan')
                tdl.add_xpath('rowspan', './@rowspan')
                row_loaders.append(tdl)
            tl.add_value('body', [row_loaders])

        return tl.load_item()
