from distutils.util import strtobool

import scrapy
from furl import furl

from sentiment_ru.items import ReviewLoader


class VseprosportSpider(scrapy.Spider):
    name = 'vseprosport'
    allowed_domains = ['vseprosport.ru']
    crawl_deep = False

    def start_requests(self):
        url = 'https://www.vseprosport.ru/reyting-bukmekerov/'
        yield scrapy.Request(url, callback=self.parse_subjects)

    def parse_subjects(self, response):
        subject_blocks = response.css('.bookmakers-list .list-item')
        for sb in subject_blocks:
            subject_urls = sb.css('a::attr(href)').re(r'/(reyting-bukmekerov/\w+)/?')
            if not subject_urls:
                continue
            subject_url = subject_urls[0]
            subject_id = subject_url.split('/')[-1]
            subject_name = sb.css('.img::attr(title)').get()

            url = 'https://www.vseprosport.ru/get-bookmaker-comments-html'
            query = {'book': subject_id, 'offsetNews': 0}
            yield response.follow(
                url=furl(url, query=query).url,
                callback=self.parse_reviews,
                cb_kwargs={
                    'subject_name': subject_name,
                    'subject_url': subject_url,
                },
            )

    def parse_reviews(self, response, subject_name: str, subject_url: str):
        review_blocks = response.css('body > li')
        if not review_blocks:
            return
        for rb in review_blocks:
            rl = ReviewLoader(selector=rb)
            rl.add_css('id', '.answers::attr(data-vps-comment-list)', re=r'\d+$')
            rl.add_xpath('author', './figure//h4/text()')
            rl.add_xpath('content', './p[has-class("message")]/text()')
            rl.add_xpath('rating', './figure//div[has-class("star-rate")]/ul/b/text()', re=r'^(\d+)')
            rl.add_value('rating_max', 5)
            rl.add_value('rating_min', 1)
            rl.add_value('subject', subject_name)
            rl.add_xpath('time', './/p[has-class("date")]/text()')
            rl.add_value('type', 'review')
            rl.add_value('url', response.urljoin(subject_url))
            yield rl.load_item()

        if strtobool(str(self.crawl_deep)):
            f = furl(response.request.url)
            f.args['offsetNews'] = int(f.args['offsetNews']) + 5
            yield response.request.replace(url=f.url)
