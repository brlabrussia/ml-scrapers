import scrapy

from banks.items import AutoCreditLoader


class BankiAutoCreditsSpider(scrapy.Spider):
    name = 'banki_auto_credits'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        url = 'https://www.banki.ru/banks/'
        yield scrapy.Request(url, self.parse_banks)

    def parse_banks(self, response):
        pattern = r'/products/autocredits/[^/]+/'
        for link in response.css('td a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_links)
        next_page = response.css('.icon-arrow-right-16::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_banks)

    def parse_links(self, response):
        pattern = r'/products/autocredits/credit/\d+/'
        for link in response.css('a::attr(href)').re(pattern):
            yield response.follow(link, self.parse_items)

    def parse_items(self, response):
        sel = (
            '//*[has-class("definition-list__item")]'
            '/*[has-class("definition-list__title")][starts-with(normalize-space(text()), "{}")]'
            '/following-sibling::*[has-class("definition-list__desc")][1]{}'
        )
        as_text = '/text()'
        as_list = '//ul/li/text()'

        loader = AutoCreditLoader(response=response)
        loader.add_value('banki_url', response.url)
        loader.add_css('banki_bank_url', '.stella a::attr(href)', re=r'/banks/bank/[^/]+/')
        loader.add_xpath('auto_seller', sel.format('Продавец', as_list))
        loader.add_xpath('auto_seller', sel.format('Продавец', as_text))
        loader.add_xpath('auto_kind', sel.format('Вид транспортного средства', as_text))
        loader.add_xpath('auto_type', sel.format('Тип транспортного средства', as_list))
        loader.add_xpath('auto_type', sel.format('Тип транспортного средства', as_text))
        loader.add_xpath('auto_age', sel.format('Возраст транспортного средства', as_text))
        loader.add_xpath('autocredit_min_time', sel.format('Срок кредита', as_text), re=r'([^—]+)—')
        loader.add_xpath('autocredit_max_time', sel.format('Срок кредита', as_text), re=r'—([^—]+)')
        loader.add_xpath('autocredit_currency', sel.format('Валюта', as_text))
        loader.add_xpath('autocredit_amount_min', sel.format('Сумма кредита', as_text), re=r'([^—]+)—')
        loader.add_xpath('autocredit_amount_min', sel.format('Сумма кредита', as_text), re=r'от\xa0([\d\xa0]+)')
        loader.add_xpath('autocredit_amount_max', sel.format('Сумма кредита', as_text), re=r'—([^—]+)')
        loader.add_xpath('min_down_payment', sel.format('Минимальный первоначальный взнос', as_text), re=r'([\d,.]+)%')
        loader.add_xpath('loan_rate_min', sel.format('Cтавка по кредиту', as_text), re=r'([\d,.]+)—')
        loader.add_xpath('loan_rate_min', sel.format('Cтавка по кредиту', as_text), re=r'([\d,.]+)%')
        loader.add_xpath('loan_rate_max', sel.format('Cтавка по кредиту', as_text), re=r'—([\d,.]+)%')
        loader.add_xpath('loan_rate_max', sel.format('Cтавка по кредиту', as_text), re=r'([\d,.]+)%')
        loader.add_xpath('loan_rate_description', sel.format('Cтавка по кредиту', as_text))
        loader.add_xpath('autocredit_comission', sel.format('Комиссии при рассмотрении', as_text))
        loader.add_xpath('early_moratorium_repayment', sel.format('Мораторий на досрочное погашение', as_text))
        loader.add_xpath('prepayment_penalty', sel.format('Штраф за досрочное погашение', as_text))
        loader.add_xpath('insurance_necessity', sel.format('Необходимость страхования', as_text))
        loader.add_xpath('borrowers_age', sel.format('Возраст заёмщика', as_text))
        loader.add_xpath('income_proof', sel.format('Подтверждение дохода', as_list))
        loader.add_xpath('registration_requirements', sel.format('Регистрация по месту получения кредита', as_text))
        loader.add_xpath('last_work_experience', sel.format('Стаж работы на последнем месте', as_text))
        loader.add_xpath('full_work_experience', sel.format('Стаж работы общий', as_text))
        loader.add_xpath('additional_conditions', sel.format('Особые условия', as_text))
        loader.add_xpath('updated_at', sel.format('Дата актуализации', as_text))

        yield loader.load_item()
