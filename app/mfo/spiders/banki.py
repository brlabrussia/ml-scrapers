import re

import scrapy


class BankiSpider(scrapy.Spider):
    name = 'banki'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/microloans/companies/'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        css = '*[data-test=mfo-item-company]::attr(href)'
        for link in response.css(css):
            yield response.follow(link, self.parse_subject)

    def parse_subject(self, response):
        css = '*[data-test=mfo-widget] tbody tr td:first-child a::attr(href)'
        for link in response.css(css).getall():
            yield response.follow(link, self.parse_product)

    def parse_product(self, response):
        def get_value_for_field(field):
            xp = f'//*[has-class("definition-list__key")][normalize-space(text())="{field}"]/../*[has-class("definition-list__value")]/text()'
            value = response.xpath(xp).get()
            if value:
                value = re.sub(r'\s+', ' ', value).strip()
            return value

        def get_value_list_for_field(field):
            xp = f'//*[has-class("definition-list__key")][normalize-space(text())="{field}"]/../*[has-class("definition-list__value")]/ul/li/text()'
            return response.xpath(xp).getall()

        def get_note_for_field(field):
            xp = f'//*[has-class("definition-list__key")][normalize-space(text())="{field}"]/../*[has-class("definition-list__value")]/*[has-class("text-note")]/p/text()'
            return response.xpath(xp).get()

        yield {
            'subject': response.css('h1::text').get(),
            'url': response.url,
            'max_money_value': get_value_for_field('Сумма займа'),
            'first_loan_condition': get_note_for_field('Сумма займа'),
            'dates': get_value_for_field('Срок'),
            'rate': get_value_for_field('Ставка'),
            'issuance': get_value_for_field('Срок выдачи'),
            'loan_purpose': get_value_list_for_field('Цель займа'),
            'loan_time_terms': get_note_for_field('Срок'),
            'loan_providing': get_value_list_for_field('Обеспечение'),
            'borrowers_categories': get_value_list_for_field('Категория заемщиков'),
            'borrowers_age': get_value_for_field('Возраст заемщика'),
            'borrowers_registration': get_value_list_for_field('Регистрация'),
            'borrowers_documents': get_value_list_for_field('Документы'),
            'loan_processing': get_value_list_for_field('Оформление займа'),
            'loan_form': get_value_list_for_field('Форма выдачи'),
            'loan_form_description': get_note_for_field('Форма выдачи'),
            'repayment_order': get_value_list_for_field('Порядок погашения'),
            'repayment_order_description': get_note_for_field('Порядок погашения'),
            'payment_methods': get_value_list_for_field('Способ оплаты'),
            'organization': {
                'trademark': get_value_for_field('Торговая марка'),
                'legal_entity': get_value_for_field('Юридическое лицо'),
                'head_name': get_value_for_field('Руководитель'),
                'address': get_value_for_field('Адрес'),
                'ogrn': get_value_for_field('ОГРН'),
                'reg_number': get_value_for_field('Рег. номер'),
                'phone': get_value_for_field('Телефон'),
                'website': get_value_for_field('Официальный сайт'),
            },
        }
