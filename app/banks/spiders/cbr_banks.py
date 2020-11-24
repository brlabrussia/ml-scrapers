import scrapy

from banks.items import CbrBankLoader, format_date


class CbrBanksSpider(scrapy.Spider):
    name = 'cbr_banks'
    allowed_domains = ['cbr.ru']

    def start_requests(self):
        url = 'http://cbr.ru/banking_sector/credit/FullCoList/'
        yield scrapy.Request(url, self.parse_links)

    def parse_links(self, response):
        for link in response.css('td a::attr(href)'):
            yield response.follow(link, self.parse_bank)

    def parse_bank(self, response):
        cbl = CbrBankLoader(response=response)

        xp = '//*[has-class("coinfo_item_title")][starts-with(normalize-space(text()), "{}")]/following-sibling::div[has-class("coinfo_item_text")][1]/text()'
        cbl.add_value('cbr_url', response.url)
        cbl.add_xpath('full_name', xp.format('Полное фирменное наименование'))
        cbl.add_xpath('name', xp.format('Сокращённое фирменное наименование'))
        cbl.add_xpath('reg_number', xp.format('Регистрационный номер'))
        cbl.add_xpath('registration_date', xp.format('Дата регистрации Банком России'))
        cbl.add_xpath('ogrn', xp.format('Основной государственный регистрационный номер'), re=r'\d{5,}')
        cbl.add_xpath('ogrn_date', xp.format('Основной государственный регистрационный номер'), re=r'\d{2}\.\d{2}\.\d{4}')
        cbl.add_xpath('bik', xp.format('БИК'))
        cbl.add_xpath('statutory_address', xp.format('Адрес из устава'))
        cbl.add_xpath('actual_address', xp.format('Адрес фактический'))
        cbl.add_xpath('tel_number', xp.format('Телефон'))
        cbl.add_xpath('statutory_update', xp.format('Устав'), re=r'\d{2}\.\d{2}\.\d{4}')
        cbl.add_xpath('authorized_capital', xp.format('Уставный капитал'), re=r'^[\d\s]*')
        cbl.add_xpath('authorized_capital_date', xp.format('Уставный капитал'), re=r'\d{2}\.\d{2}\.\d{4}')
        cbl.add_xpath('license_info', xp.format('Лицензия (дата выдачи/последней замены)'))
        cbl.add_xpath('license_info', xp.format('Лицензия (дата выдачи/последней замены)').replace('/text()', '/*/text()'))
        cbl.add_xpath('license_info_file', xp.format('Лицензия (дата выдачи/последней замены)').replace('/text()', '/p/a/@href'))
        cbl.add_xpath('deposit_insurance_system', xp.format('Участие в системе страхования вкладов'))
        cbl.add_xpath('english_name', xp.format('Фирменное наименование на английском языке'))

        xp = '//h4[starts-with(normalize-space(text()), "Подразделения кредитной организации")]/following-sibling::div[1]//td[starts-with(normalize-space(text()), "{}")]/following-sibling::td[1]/text()'
        cbl.add_xpath('bank_subsidiaries', xp.format('Филиалы'))
        cbl.add_xpath('bank_agencies', xp.format('Представительства'), re=r'\d+')
        cbl.add_xpath('additional_offices', xp.format('Дополнительные офисы'), re=r'\d+')
        cbl.add_xpath('operating_cash_desks', xp.format('Операционные кассы вне кассового узла'), re=r'\d+')
        cbl.add_xpath('operating_offices', xp.format('Операционные офисы'), re=r'\d+')
        cbl.add_xpath('mobile_cash_desks', xp.format('Передвижные пункты кассовых операций'), re=r'\d+')

        cbl.add_css('info_sites', '.org_info ._links a::attr(href)')
        cbl.add_value('cards', self.extract_cards(response))
        cbl.add_value('subsidiaries', self.extract_subsidiaries(response))
        cbl.add_value('agencies', self.extract_agencies(response))

        yield cbl.load_item()

    def extract_cards(self, response):
        ret = []
        for row_sel in response.css('.cards table tr'):
            data_sels = row_sel.css('td')
            if len(data_sels) != 3:
                continue
            ret.append({
                'pay_system': data_sels[0].css('::text').get(),
                'emission': True if 'black_dot' in data_sels[1].get() else False,
                'acquiring': True if 'black_dot' in data_sels[2].get() else False,
            })
        return ret

    def extract_subsidiaries(self, response):
        ret = []
        table_sel = response.xpath('//h2[starts-with(normalize-space(text()), "Филиалы")]/following-sibling::div[1]//table')
        for row_sel in table_sel.css('tr'):
            data_sels = row_sel.css('td')
            if len(data_sels) != 4:
                continue
            ret.append({
                'reg_number': data_sels[0].css('::text').get(),
                'name': data_sels[1].css('::text').get(),
                'reg_date': format_date(data_sels[2].css('::text').get()),
                'address': data_sels[3].css('::text').get(),
            })
        return ret

    def extract_agencies(self, response):
        ret = []
        table_sel = response.xpath('//h2[starts-with(normalize-space(text()), "Представительства")]/following-sibling::div[1]//table')
        for row_sel in table_sel.css('tr'):
            data_sels = row_sel.css('td')
            if len(data_sels) != 4:
                continue
            ret.append({
                'name': data_sels[1].css('::text').get(),
                'foundation_date': format_date(data_sels[2].css('::text').get()),
                'address': data_sels[3].css('::text').get(),
            })
        return ret
