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
            self.parse_subjects,
            args=self.splash_args,
        )

    def parse_subjects(self, response):
        subject_blocks = response.css('.rb-tbody > tr')
        for sb in subject_blocks:
            subject_url = sb.css('.td-view > a::attr(href)').get()
            yield scrapy_splash.SplashRequest(
                subject_url,
                self.parse_ratings,
                args=self.splash_args,
            )

    def parse_ratings(self, response):
        def get_rating_for_field(field):
            xp = f'//*[has-class("beton_bk_hars_line_title")][normalize-space(text())="{field}"]/../*[has-class("beton_bk_hars_line_count")]/text()'
            return response.xpath(xp).get()

        # Skip subject if there's no ratings table
        if not response.css('.beton_bk_hars').get():
            self.logger.debug(f"Can't find ratings table for {response.url}")
            return

        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', '.section-title::text')
        rl.add_value('min', 0)
        rl.add_value('max', 5)
        rl.add_css('experts', '#overview-main .beton_bk_head_new_stars_reit::text')
        rl.add_value('reliability', get_rating_for_field('Надежность'))
        rl.add_value('variety', get_rating_for_field('Линия в прематче'))
        rl.add_value('ratio', get_rating_for_field('Коэффициенты'))
        rl.add_value('withdrawal', get_rating_for_field('Удобство платежей'))
        rl.add_value('support', get_rating_for_field('Служба поддержки'))
        yield rl.load_item()
