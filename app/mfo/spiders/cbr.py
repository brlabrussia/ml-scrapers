import io

import openpyxl
import scrapy


class CbrSpider(scrapy.Spider):
    name = 'cbr'
    allowed_domains = ['cbr.ru']

    def start_requests(self):
        url = 'https://www.cbr.ru/vfs/finmarkets/files/supervision/list_MFO.xlsx'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        workbook = openpyxl.load_workbook(io.BytesIO(response.body))
        for row in workbook.active.iter_rows(min_row=6, values_only=True):
            yield {
                'reg_number': '-'.join(row[1:6]),
                'registry_date': row[6],
                'mfo_type': row[8],
                'ogrn': row[9],
                'inn': row[10],
                'full_name': row[11],
                'name': row[12],
                'address': row[13],
                'url': row[14],
                'email': row[15],
            }
