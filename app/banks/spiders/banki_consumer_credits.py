import json
from urllib.parse import unquote, urlparse

import scrapy
from scrapy.loader.processors import Identity, Join, MapCompose

from banks.items import ConsumerCredit
from default.items import DefaultLoader
from default.utils import format_date, format_url, normalize_space


class Loader(DefaultLoader):
    default_item_class = ConsumerCredit

    banki_bank_url_in = MapCompose(format_url)
    borrowers_age_men_out = borrowers_age_women_out = Join()
    work_experience_description_out = Join()
    updated_at_in = MapCompose(format_date)

    _ = \
        borrowers_category_out = \
        borrowers_documents_in = \
        borrowers_documents_out = \
        borrowers_income_documents_in = \
        borrowers_income_documents_out = \
        borrowers_registration_out = \
        credit_fee_description_in = \
        credit_fee_in = \
        credit_fee_out = \
        credit_insurance_in = \
        credit_insurance_out = \
        early_repayment_full_out = \
        early_repayment_partial_out = \
        loan_delivery_order_out = \
        loan_delivery_type_out = \
        loan_processing_terms_out = \
        loan_purpose_out = \
        loan_security_in = \
        loan_security_out = \
        payment_method_out = \
        rates_table_in = rates_table_out = \
        repayment_procedure_out = \
        work_experience_out = \
        Identity()


class Spider(scrapy.Spider):
    name = 'banki_consumer_credits'
    allowed_domains = ['banki.ru']
    custom_settings = {'LOG_LEVEL': 'INFO'}

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
        as_list_pairs_note = '/*[has-class("text-note")]/text()'

        def as_list_pairs(field):
            ret = [
                {
                    ' '.join([
                        (el.xpath('normalize-space(text())').get() or ''),
                        (el.xpath('normalize-space(.//*[not(has-class("text-note"))]//text())').get() or ''),
                    ]):
                    (el.css('.text-note::text').get() or ''),
                }
                for el in response.xpath(sel.format(field, '//ul/li'))
            ]
            ret = [
                {normalize_space(k): normalize_space(v) for k, v in d.items()}
                for d in ret
            ]
            ret = [d for d in ret if d != {'': ''}]
            return ret

        def as_list_pairs2(field):
            ret = [
                {
                    ' '.join([
                        (el.xpath('text()').get() or ''),
                        (el.xpath('.//*[not(has-class("text-note"))]//text()').get() or ''),
                    ]):
                    (el.xpath('.//*[has-class("text-note")]/text()').get() or ''),
                }
                for el in response.xpath(sel.format(field, '/div/div[not(has-class("text-note"))]'))
            ]
            if not ret:
                ret = [{(response.xpath(sel.format(field, '/text()')).get() or ''): ''}]
            ret = [
                {normalize_space(k): normalize_space(v) for k, v in d.items()}
                for d in ret
            ]
            ret = [d for d in ret if d != {'': ''}]
            return ret

        def as_list_pairs4(field):
            ret = [
                {
                    ' '.join([
                        (el.xpath('text()').get() or ''),
                        (el.xpath('.//*[not(has-class("text-note"))]//text()').get() or ''),
                    ]):
                    (el.css('.text-note::text').get() or ''),
                }
                for el in response.xpath(sel.format(field, '/ul/li'))
            ]
            ret = [
                {normalize_space(k): normalize_space(v) for k, v in d.items()}
                for d in ret
            ]
            ret = [d for d in ret if d != {'': ''}]
            return ret

        def extract_credit_fee(sel):
            sel = '//*[has-class("definition-list__item")][@data-currency-id="{}"]' + sel
            field = 'Комиссии'
            ret = {}
            for currency in ['RUB', 'USD', 'EUR']:
                val = [
                    {
                        ' '.join([
                            (''.join(el.xpath('./text()').getall()) or ''),
                            (el.xpath('normalize-space(.//*[not(has-class("text-note"))]//text())').get() or ''),
                        ]):
                        (el.css('.text-note::text').get() or ''),
                    }
                    for el in response.xpath(sel.format(currency, field, '//ul/li'))
                ]
                if not val:
                    val = [{(response.xpath(sel.format(currency, field, '/text()')).get() or ''): ''}]
                val = [
                    {normalize_space(k): normalize_space(v) for k, v in d.items()}
                    for d in val
                ]
                val = [d for d in val if d != {'': ''}]
                if not val:
                    continue
                ret[currency] = val
            return ret or None

        def extract_credit_fee_description(sel):
            sel = '//*[has-class("definition-list__item")][@data-currency-id="{}"]' + sel
            field = 'Комиссии'
            ret = {}
            for currency in ['RUB', 'USD', 'EUR']:
                val = response.xpath(sel.format(currency, field, as_list_pairs_note)).get()
                if not val:
                    continue
                ret[currency] = val
            return ret or None

        loader = Loader(response=response)
        loader.add_value('banki_url', response.url)
        loader.add_xpath('banki_bank_url', '//h1/ancestor::header/following-sibling::div//a/@href')
        loader.add_css('name_base', '.bread-crumbs__item:last-child *::text')
        loader.add_css('name_full', 'h1[data-test=header]::text')

        try:
            module_options = response.css('[data-module*=CreditsBundle]::attr(data-module-options)').get()
            module_options_obj = json.loads(unquote(module_options))
            loader.add_value('rates_table', module_options_obj['rateTable'])
        except Exception:
            self.logger.info(f'Cannot process rates module options for: {response.url}')

        loader.add_xpath('account_currency', sel.format('Валюта счета', as_text))
        loader.add_xpath('loan_purpose', sel.format('Цель кредита', as_list))
        loader.add_xpath('loan_purpose_description', sel.format('Цель кредита', as_note))
        loader.add_value('credit_fee', extract_credit_fee(sel))
        loader.add_value('credit_fee_description', extract_credit_fee_description(sel))
        loader.add_value('loan_security', as_list_pairs2('Обеспечение'))
        loader.add_xpath('loan_security_description', sel.format('Обеспечение', '/*/*[has-class("text-note")]/text()'))
        loader.add_xpath('loan_security_description', sel.format('Обеспечение', as_list_pairs_note))
        loader.add_value('credit_insurance', as_list_pairs('Страхование'))
        loader.add_xpath('credit_insurance_description', sel.format('Страхование', as_list_pairs_note))
        loader.add_xpath('additional_information', sel.format('Дополнительная информация', as_text))
        loader.add_xpath('borrowers_category', sel.format('Категория заемщиков', as_list))
        loader.add_xpath('borrowers_age_men', sel.format('Возраст заемщика', as_sublist.format('для мужчин')))
        loader.add_xpath('borrowers_age_women', sel.format('Возраст заемщика', as_sublist.format('для женщин')))
        loader.add_xpath('work_experience', sel.format('Стаж работы', as_list))
        loader.add_xpath('work_experience_description', sel.format('Стаж работы', '//*[has-class("text-note")]//text()'))
        loader.add_xpath('borrowers_registration', sel.format('Регистрация', as_list))
        loader.add_xpath('borrowers_income_description', sel.format('Доход', as_text))
        loader.add_xpath('borrowers_income_tip', sel.format('Доход', as_note))
        loader.add_value('borrowers_income_documents', as_list_pairs('Доход'))
        loader.add_value('borrowers_documents', as_list_pairs4('Документы'))
        loader.add_xpath('borrowers_documents_description', sel.format('Документы', '/div/ul/li/text()'))
        loader.add_xpath('application_consider_time', sel.format('Срок рассмотрения заявки', as_text))
        loader.add_xpath('application_consider_time_description', sel.format('Срок рассмотрения заявки', as_note))
        loader.add_xpath('credit_decision_time', sel.format('Максимальный срок действия кредитного решения', as_text))
        loader.add_xpath('loan_processing_terms', sel.format('Оформление кредита', as_list))
        loader.add_xpath('loan_delivery_order', sel.format('Режим выдачи', as_list))
        loader.add_xpath('loan_delivery_order_description', sel.format('Режим выдачи', as_list_pairs_note))
        loader.add_xpath('loan_delivery_type', sel.format('Форма выдачи', as_list))
        loader.add_xpath('loan_delivery_type_description', sel.format('Форма выдачи', as_list_pairs_note))
        loader.add_xpath('repayment_procedure', sel.format('Порядок погашения', as_list))
        loader.add_xpath('repayment_procedure_description', sel.format('Порядок погашения', as_list_pairs_note))
        loader.add_xpath('early_repayment_full', sel.format('Досрочное погашение', as_sublist.format('полное')))
        loader.add_xpath('early_repayment_partial', sel.format('Досрочное погашение', as_sublist.format('частичное')))
        loader.add_xpath('obligations_violation', sel.format('Нарушение обязательств по кредиту', as_text))
        loader.add_xpath('payment_method', sel.format('Способ оплаты', as_list))
        loader.add_css('updated_at', '[data-test=read-more]', re=r'Дата актуализации: (.+)\. ')

        yield loader.load_item()
