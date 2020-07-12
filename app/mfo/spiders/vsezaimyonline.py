import scrapy


class VsezaimyonlineSpider(scrapy.Spider):
    name = 'vsezaimyonline'
    allowed_domains = ['vsezaimyonline.ru']

    def start_requests(self):
        url = 'https://vsezaimyonline.ru/mfo'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        for link in response.css('.company_title::attr(href)'):
            yield response.follow(link, self.parse_info)

    def parse_info(self, response):
        item = {
            'subject': response.css('.zaym-name::text').get(),
            'url': response.url,
            'props': {},
        }
        prop_name_blocks = response.css('#single_content_wrap .left-block li')
        for pnb in prop_name_blocks:
            prop_name = pnb.css('::text').get()
            prop_data_id = pnb.css('::attr(data-id)').get()
            prop_value_block = response.css(f'#single_content_wrap .right-block div[data-id="{prop_data_id}"]')
            prop_value = {
                'list': [
                    ''.join(list_item.css('*::text').getall())
                    for list_item in prop_value_block.css('li')
                ],
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
