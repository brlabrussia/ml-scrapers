import io

import openpyxl
import scrapy

from mfodb.items import CbrLoader


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
            cl.add_value('reg_number', ''.join(row[1:6]))
            cl.add_value('registry_date', row[6])
            cl.add_value('mfo_type', row[8])
            cl.add_value('ogrn', row[9])
            cl.add_value('inn', row[10])
            cl.add_value('full_name', row[11])
            cl.add_value('name', row[12])
            cl.add_value('address', row[13])
            cl.add_value('url', row[14])
            cl.add_value('email', row[15])
            yield cl.load_item()
