import io

import openpyxl
import scrapy

from mfo.items import CbrLoader


class CbrSpider(scrapy.Spider):
    name = 'cbr'
    allowed_domains = ['cbr.ru']

    def start_requests(self):
        url = 'https://www.cbr.ru/vfs/finmarkets/files/supervision/list_MFO.xlsx'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        workbook = openpyxl.load_workbook(io.BytesIO(response.body))
        for row in workbook.active.iter_rows(min_row=6, values_only=True):
            cl = CbrLoader()
            cl.add_value('scraped_from', response.url)
            cl.add_value('cbrn', ''.join(row[1:6]), re=r'\d{13}$')
            cl.add_value('cbr_created_at', row[6])
            cl.add_value('type', row[8])
            cl.add_value('ogrn', row[9], re=r'\d{13}$')
            cl.add_value('inn', row[10], re=r'\d{10}$')
            cl.add_value('name_full', row[11])
            cl.add_value('name_short', row[12])
            cl.add_value('address', row[13])
            cl.add_value('website', row[14], re=r'^((https?://)?([а-я.-]+|[a-z.-]+)\.(рф|ru|com|net))$')
            cl.add_value('email', row[15], re=r'^(([а-я.-]+|[a-z.-]+)@.+\.(рф|ru|com|net))$')
            yield cl.load_item()
