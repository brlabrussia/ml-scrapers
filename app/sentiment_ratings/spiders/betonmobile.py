import scrapy
import scrapy_splash

from sentiment_ratings.items import RatingLoader


class BetonmobileSpider(scrapy.Spider):
    name = 'betonmobile'
    allowed_domains = ['betonmobile.ru']
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES': 20,  # splash is reloaded on RAM and it takes time
        'DOWNLOAD_DELAY': 0.25,  # wait between retries
    }
    splash_args = {'wait': 5, 'images': 0}

    def start_requests(self):
        url = 'https://betonmobile.ru/vse-bukmekerskie-kontory'
        yield scrapy_splash.SplashRequest(
            url,
            self.parse_links,
            args=self.splash_args,
        )

    def parse_links(self, response):
        subject_blocks = response.css('.rb-tbody_new > tr')
        for sb in subject_blocks:
            subject_url = sb.css('.td-view_new > a::attr(href)').get()
            yield scrapy_splash.SplashRequest(
                subject_url,
                self.parse_items,
                args=self.splash_args,
            )

    def parse_items(self, response):
        # Skip subject if there's no ratings table
        if not response.css('.beton_bk_hars'):
            self.logger.debug(f'Cannot find ratings table for {response.url}')
            return

        sel = (
            '//*[has-class("beton_bk_hars_line_title")][normalize-space(text())="{}"]'
            '/../*[has-class("beton_bk_hars_line_count")]/text()'
        )
        loader = RatingLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_css('subject', '.section-title::text')
        loader.add_value('min', 0)
        loader.add_value('max', 5)
        loader.add_css('experts', '#overview-main .beton_bk_head_new_stars_reit::text')
        loader.add_xpath('reliability', sel.format('Надежность'))
        loader.add_xpath('variety', sel.format('Линия в прематче'))
        loader.add_xpath('variety', sel.format('Линия в лайве'))
        loader.add_xpath('ratio', sel.format('Коэффициенты'))
        loader.add_xpath('withdrawal', sel.format('Удобство платежей'))
        loader.add_xpath('support', sel.format('Служба поддержки'))
        yield loader.load_item()
