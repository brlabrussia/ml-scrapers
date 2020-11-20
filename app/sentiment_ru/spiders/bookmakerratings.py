from distutils.util import strtobool

import scrapy
from furl import furl

from sentiment_ru.items import ReviewLoader


class BookmakerratingsSpider(scrapy.Spider):
    name = 'bookmakerratings'
    allowed_domains = ['bookmaker-ratings.ru']
    custom_settings = {'CONCURRENT_REQUESTS': 1}
    crawl_deep = False

    def start_requests(self):
        url = 'https://bookmaker-ratings.ru/bookmakers-homepage/vse-bukmekerskie-kontory/'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.table-container .table-row')
        for sb in subject_blocks:
            subject_id = sb.css('::attr(data-id)').get()
            subject_name = sb.css('::attr(data-name)').get()
            subject_url = sb.css('.feed-link::attr(href)').get()
            yield scrapy.Request(
                method='POST',
                url='https://bookmaker-ratings.ru/wp-admin/admin-ajax.php',
                body=f'action=feedbacks_items_page&page=1&post_id={subject_id}',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                callback=self.parse_reviews,
                cb_kwargs={
                    'subject_name': subject_name,
                    'subject_url': subject_url,
                },
            )

    def parse_reviews(self, response, subject_name: str, subject_url: str):
        review_blocks = response.css('div.single')
        if not review_blocks:
            return
        for rb in review_blocks:
            rl = ReviewLoader(selector=rb)
            rl.add_css('id', '::attr(id)', re=r'\d+$')
            rl.add_css('author', '.namelink::text')
            rl.add_css('content', '.content .text > *::text')
            rl.add_value('language', 'ru')
            rl.add_css('rating', '.feedbacks-rating-stars .num::text')
            rl.add_value('rating_max', 5)
            rl.add_value('rating_min', 1)
            rl.add_value('subject', subject_name)
            rl.add_css('time', '.date::text')
            rl.add_value('type', 'review')
            rl.add_value('url', subject_url)
            yield rl.load_item()

        if strtobool(str(self.crawl_deep)):
            f = furl(args=response.request.body.decode())
            f.args['page'] = int(f.args['page']) + 1
            yield response.request.replace(body=f.querystr)
