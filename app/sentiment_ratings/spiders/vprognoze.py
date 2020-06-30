import scrapy
import scrapy_splash

from sentiment_ratings.items import RatingLoader


class VprognozeSpider(scrapy.Spider):
    name = 'vprognoze'
    allowed_domains = ['vprognoze.ru']
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES': 20,  # splash is reloaded on RAM and it takes time
        'DOWNLOAD_DELAY': 0.25,  # wait between retries
    }
    splash_args = {'wait': 5, 'images': 0}

    def start_requests(self):
        url = 'https://vprognoze.ru/rating/'
        yield scrapy_splash.SplashRequest(
            url,
            self.parse_subjects,
            args=self.splash_args,
        )

    def parse_subjects(self, response):
        subject_blocks = response.css('.shot_info_kontora')
        for sb in subject_blocks:
            subject_url = sb.css('.review_btn_vp a::attr(href)').get()
            yield scrapy_splash.SplashRequest(
                subject_url,
                self.parse_ratings,
                args=self.splash_args,
            )

    def parse_ratings(self, response):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', 'h1::text')
        rl.add_value('min', 0)
        rl.add_value('max', 10)
        rl.add_css('reliability', '.border_bl3 .static::text', re=r'([\d.]+).')
        rl.add_css('variety', '.border_bl2 .static::text', re=r'([\d.]+).')
        rl.add_css('ratio', '.border_bl1 .static::text', re=r'([\d.]+).')
        rl.add_css('withdrawal', '.border_bl4 .static::text', re=r'([\d.]+).')
        yield rl.load_item()
