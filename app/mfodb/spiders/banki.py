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
        bl.add_value('url', response.url)
        bl.add_css('name', 'h1::text')
        bl.add_css('logo', '[data-test=mfo-logo]::attr(src)')
        bl.add_xpath('updated_at', '//*[has-class("text-note")][starts-with(normalize-space(text()), "Дата актуализации")]/text()', re=r'\d{2}\.\d{2}\.\d{4} \d+:\d{2}')
        # * О займе
        # ** Условия и ставки
        bl.add_xpath('loan_purpose', xp.format('Цель займа', as_list))
        bl.add_xpath('max_money_value', xp.format('Сумма займа', as_text), re=r'до ([\d ]+)')
        bl.add_xpath('first_loan_condition', xp.format('Сумма займа', as_note))
        bl.add_xpath('rate', xp.format('Ставка', as_text))  # re=r'([\d\,]+)'
        bl.add_xpath('dates_from', xp.format('Срок', as_text), re=r'от (\d+)')  # either 'от 1 до 365 дней'
        bl.add_xpath('dates_from', xp.format('Срок', as_text), re=r'^(\d+) дней')  # or '7 дней'
        bl.add_xpath('dates_to', xp.format('Срок', as_text), re=r'до (\d+)')  # either 'от 1 до 365 дней'
        bl.add_xpath('dates_to', xp.format('Срок', as_text), re=r'^(\d+) дней')  # or '7 дней'
        bl.add_xpath('loan_time_terms', xp.format('Срок', as_note))
        bl.add_xpath('loan_providing', xp.format('Обеспечение', as_list))
        # ** Требования и документы
        bl.add_xpath('borrowers_categories', xp.format('Категория заемщиков', as_list))
        bl.add_xpath('borrowers_age', xp.format('Возраст заемщика', as_text))
        bl.add_xpath('borrowers_registration', xp.format('Регистрация', as_list))
        bl.add_xpath('borrowers_documents', xp.format('Документы', as_list))
        # ** Выдача
        bl.add_xpath('issuance', xp.format('Срок выдачи', as_text))
        bl.add_xpath('loan_processing', xp.format('Оформление займа', as_list))
        bl.add_xpath('loan_form', xp.format('Форма выдачи', as_list))
        bl.add_xpath('loan_form_description', xp.format('Форма выдачи', as_note))
        # ** Погашение
        bl.add_xpath('repayment_order', xp.format('Порядок погашения', as_list))
        bl.add_xpath('repayment_order_description', xp.format('Порядок погашения', as_note))
        bl.add_xpath('payment_methods', xp.format('Способ оплаты', as_list))
        # * Об организации
        bl.add_xpath('trademark', xp.format('Торговая марка', as_text))
        bl.add_xpath('head_name', xp.format('Руководитель', as_text))
        bl.add_xpath('address', xp.format('Адрес', as_text))
        bl.add_xpath('ogrn', xp.format('ОГРН', as_text), re=r'\d{5,}')
        bl.add_xpath('reg_number', xp.format('Рег. номер', as_text), re=r'\d{5,}')
        bl.add_xpath('website', xp.format('Официальный сайт', '/a/text()'))
        yield bl.load_item()

    def parse_product_old(self, response):
        item = {
            'subject': response.css('h1::text').get(),
            'url': response.url,
            'logo': response.css('[data-test=mfo-logo]::attr(src)').get(),
            'actualization': response.xpath('//*[has-class("text-note")][starts-with(normalize-space(text()), "Дата актуализации")]/text()').get(),
            'props': {},
        }
        prop_blocks = response.css('.definition-list__item')
        for pb in prop_blocks:
            prop_name = pb.css('.definition-list__key::text').get()
            prop_value_block = pb.css('.definition-list__value')
            prop_value = {
                'text': prop_value_block.css('::text').get(),
                'note': prop_value_block.css('.text-note p::text').get(),
                'list': prop_value_block.css('li::text').getall(),
                'links': [
                    {
                        'text': link.css('::text').get(),
                        'href': link.css('::attr(href)').get(),
                    }
                    for link in prop_value_block.css('a')
                ],
            }
            item['props'][prop_name] = prop_value
        yield item
