import scrapy
from scrapy.http import Response

from sentiment_ru.items import ReviewLoader


class LegalbetSpider(scrapy.Spider):
    name = "legalbet"
    allowed_domains = ["legalbet.ru"]
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://legalbet.ru/bukmekerskye-kontory/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response: Response):
        xp = "//tr[@data-book-details-toggle and not(@class)]//a[@title='Отзывы']/@href"
        bookmaker_links = response.xpath(xp)
        for bookmaker_link in bookmaker_links:
            yield response.follow(bookmaker_link, callback=self.parse_reviews)

    def parse_reviews(self, response: Response):
        bookmaker_name = response.xpath("//div[has-class('title')]/a/text()").get()
        xp = "//div[has-class('review')]"
        reviews = response.xpath(xp)
        for review in reviews:
            loader = ReviewLoader(selector=review)
            loader.add_xpath("author", ".//div[has-class('author')]//a[has-class('name')]/text()")
            loader.add_xpath("content_positive", ".//div[has-class('icon-plus')]/following-sibling::div[has-class('description')][1]/text()")
            loader.add_xpath("content_negative", ".//div[has-class('icon-minus')]/following-sibling::div[has-class('description')][1]/text()")
            loader.add_value("subject", bookmaker_name)
            loader.add_xpath("time", ".//div[has-class('author')]//div[has-class('date')]/text()")
            loader.add_value("type", "review")
            loader.add_value("url", response.request.url)
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            next_page = response.xpath("//a[@data-container-id='infinite-list']/@data-url").get()
            if next_page:
                yield response.follow(next_page, callback=self.parse_reviews)
