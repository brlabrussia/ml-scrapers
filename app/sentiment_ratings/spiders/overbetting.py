import scrapy
import scrapy_splash

from sentiment_ratings.items import RatingLoader


class OverbettingSpider(scrapy.Spider):
    name = 'overbetting'
    allowed_domains = ['overbetting.ru']
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES': 20,  # splash is reloaded on RAM and it takes time
        'DOWNLOAD_DELAY': 0.25,  # wait between retries
    }
    splash_args = {'wait': 5, 'images': 0}

    def start_requests(self):
        url = 'https://overbetting.ru/bk/'
        yield scrapy_splash.SplashRequest(
            url,
            self.parse_subjects,
            args=self.splash_args,
        )

    def parse_subjects(self, response):
        subject_blocks = response.css('.bk-rating__item')
        for sb in subject_blocks:
            subject_url = sb.css('.bk-rating__buttons a:nth-child(2)::attr(href)').get()
            yield scrapy_splash.SplashRequest(
                subject_url,
                self.parse_ratings,
                args=self.splash_args,
            )

    def parse_ratings(self, response):
        rl = RatingLoader(response=response)
        rl.add_value('url', response.url)
        rl.add_css('subject', 'h1::text')
        rl.add_css('experts', '.bk-preview__stats-item.is-red .bk-preview__stats-points b::text', re=r'([\d.]+) из')
        rl.add_value('experts_min', 0)
        rl.add_css('experts_max', '.bk-preview__stats-item.is-red .bk-preview__stats-points b::text', re=r'из ([\d.]+)')
        rl.add_css('users', '.bk-preview__stats-item.is-blue .bk-preview__stats-points b::text', re=r'([\d.]+) из')
        rl.add_value('users_min', 0)
        rl.add_css('users_max', '.bk-preview__stats-item.is-blue .bk-preview__stats-points b::text', re=r'из ([\d.]+)')
        rl.add_xpath('variety', '//span[normalize-space(text())="Линия и роспись"]/../span/text()', re=r'([\d.]+) из')
        rl.add_value('variety_min', 0)
        rl.add_xpath('variety_max', '//span[normalize-space(text())="Линия и роспись"]/../span/text()', re=r'из ([\d.]+)')
        rl.add_xpath('ratio', '//span[normalize-space(text())="Коэффициенты (маржа)"]/../span/text()', re=r'([\d.]+) из')
        rl.add_value('ratio_min', 0)
        rl.add_xpath('ratio_max', '//span[normalize-space(text())="Коэффициенты (маржа)"]/../span/text()', re=r'из ([\d.]+)')
        yield rl.load_item()
