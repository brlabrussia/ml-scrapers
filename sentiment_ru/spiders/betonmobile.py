import scrapy
import scrapy_splash

from sentiment_ru.items import ReviewLoader


class BetonmobileSpider(scrapy.Spider):
    name = 'betonmobile'
    allowed_domains = ['betonmobile.ru']
    custom_settings = {'CONCURRENT_REQUESTS': 1}

    splash_args = {
        'wait': 5,
        'images': 0,
    }

    def start_requests(self):
        url = 'https://betonmobile.ru/vse-bukmekerskie-kontory'
        yield scrapy_splash.SplashRequest(
            url,
            self.parse_bookmakers,
            args=self.splash_args,
        )

    def parse_bookmakers(self, response):
        bookmaker_blocks = response.css('.rb-tbody > tr')
        for bb in bookmaker_blocks:
            comments = bb.css('.td-comments span::text').get()
            if comments == '0':
                continue
            link = bb.css('.td-view > a::attr(href)').get()
            yield scrapy_splash.SplashRequest(
                link,
                self.parse_reviews,
                args=self.splash_args,
            )

    def parse_reviews(self, response):
        subject = response.css('.section-title::text').get()
        review_blocks = response.css('.commentlist > li.comment > div.comment')
        for rb in review_blocks:
            loader = ReviewLoader(selector=rb)
            loader.add_css('author', '.comhed > .comaut::text')
            loader.add_css('content', '.comment-content > p::text')
            loader.add_value('subject', subject)
            loader.add_css('time', '.comment-meta time::attr(datetime)')
            loader.add_value('type', 'review')
            loader.add_value('url', response.url)
            yield loader.load_item()
