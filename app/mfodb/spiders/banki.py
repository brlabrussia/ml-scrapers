import scrapy

from mfodb.items import BankiLoader


class BankiSpider(scrapy.Spider):
    name = 'banki'
    allowed_domains = ['banki.ru']

    def start_requests(self):
        # url = 'https://www.banki.ru/microloans/companies/'
        # yield scrapy.Request(url, callback=self.parse_subjects)
        for i in range(1, 400):
            url = f'https://www.banki.ru/microloans/products/{i}/'
            yield scrapy.Request(url, callback=self.parse_product)

    def parse_subjects(self, response):
        css = '*[data-test=mfo-item-company]::attr(href)'
        for link in response.css(css):
            yield response.follow(link, self.parse_subject)

    def parse_subject(self, response):
        css = '*[data-test=mfo-widget] tbody tr td:first-child a::attr(href)'
        for link in response.css(css).getall():
            yield response.follow(link, self.parse_product)

    def parse_product(self, response):
        # xpath selectors constructor
        xp = '//*[has-class("definition-list__key")][normalize-space(text())="{}"]/../*[has-class("definition-list__value")]{}'
        as_text = '/text()'
        as_list = '/ul/li/text()'
        as_note = '/*[has-class("text-note")]/p/text()'

        bl = BankiLoader(response=response)
        bl.add_css('name', 'h1::text')
        bl.add_value('banki_url', response.url)
        bl.add_xpath('banki_updated_at', '//*[has-class("text-note")][starts-with(normalize-space(text()), "Дата актуализации")]/text()', re=r'\d{2}\.\d{2}\.\d{4} \d+:\d{2}')
        # * О займе
        # ** Условия и ставки
        bl.add_xpath('purposes', xp.format('Цель займа', as_list))
        bl.add_xpath('amount_min', xp.format('Сумма займа', as_text), re=r'от ([\d ]+)')
        bl.add_xpath('amount_max', xp.format('Сумма займа', as_text), re=r'до ([\d ]+)')
        bl.add_xpath('amount_note', xp.format('Сумма займа', as_note))
        bl.add_xpath('rate', xp.format('Ставка', as_text))  # re=r'([\d\,]+)'
        bl.add_xpath('period_min', xp.format('Срок', as_text), re=r'от (\d+)')  # either 'от 1 до 365 дней'
        bl.add_xpath('period_min', xp.format('Срок', as_text), re=r'^(\d+) дней')  # or '7 дней'
        bl.add_xpath('period_max', xp.format('Срок', as_text), re=r'до (\d+)')  # either 'от 1 до 365 дней'
        bl.add_xpath('period_max', xp.format('Срок', as_text), re=r'^(\d+) дней')  # or '7 дней'
        bl.add_xpath('period_note', xp.format('Срок', as_note))
        bl.add_xpath('collateral', xp.format('Обеспечение', as_list))
        # ** Требования и документы
        bl.add_xpath('borrower_categories', xp.format('Категория заемщиков', as_list))
        bl.add_xpath('borrower_age', xp.format('Возраст заемщика', as_text))
        bl.add_xpath('borrower_registration', xp.format('Регистрация', as_list))
        bl.add_xpath('borrower_documents', xp.format('Документы', as_list))
        # ** Выдача
        bl.add_xpath('application_process', xp.format('Оформление займа', as_list))
        bl.add_xpath('payment_speed', xp.format('Срок выдачи', as_text))
        bl.add_xpath('payment_forms', xp.format('Форма выдачи', as_list))
        bl.add_xpath('payment_forms_note', xp.format('Форма выдачи', as_note))
        # ** Погашение
        bl.add_xpath('repayment_process', xp.format('Порядок погашения', as_list))
        bl.add_xpath('repayment_process_note', xp.format('Порядок погашения', as_note))
        bl.add_xpath('repayment_forms', xp.format('Способ оплаты', as_list))
        # * Об организации
        bl.add_css('lender_logo', '[data-test=mfo-logo]::attr(src)')
        bl.add_xpath('lender_trademark', xp.format('Торговая марка', as_text))
        bl.add_xpath('lender_address', xp.format('Адрес', as_text))
        bl.add_xpath('lender_head_name', xp.format('Руководитель', as_text))
        bl.add_xpath('lender_cbrn', xp.format('Рег. номер', as_text), re=r'\d{13}$')
        bl.add_xpath('lender_ogrn', xp.format('ОГРН', as_text), re=r'\d{13}$')

        yield bl.load_item()
