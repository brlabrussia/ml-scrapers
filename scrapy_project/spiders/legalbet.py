import scrapy

from scrapy_project.items import ReviewLoader


class LegalbetSpider(scrapy.Spider):
    name = "legalbet"
    source_name = "Legalbet"
    allowed_domains = ["legalbet.ru"]

    def start_requests(self):
        url = "https://legalbet.ru/bukmekerskye-kontory/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//tr[@data-book-details-toggle and not(@class)]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_link = bookmaker_block.xpath(".//a[@title='Отзывы']/@href").get()
            yield response.follow(bookmaker_link, callback=self.parse_reviews)

    def parse_reviews(self, response):
        bookmaker_name = response.xpath("//div[has-class('title')]/a/text()").get()
        xp = "//div[has-class('review')]"
        reviews = response.xpath(xp)
        for review in reviews:
            loader = ReviewLoader(selector=review)

            loader.add_value("bookmaker", bookmaker_name)
            loader.add_value("source", self.source_name)

            loader.add_value("content", "")
            loader.add_value("title", "")
            loader.add_value("comment", "")
            loader.add_xpath("pluses", ".//div[has-class('icon-plus')]/following-sibling::div[has-class('description')][1]/text()")
            loader.add_xpath("minuses", ".//div[has-class('icon-minus')]/following-sibling::div[has-class('description')][1]/text()")

            loader.add_value("rating", "")
            loader.add_xpath("username", ".//div[has-class('author')]//a[has-class('name')]/text()")
            loader.add_xpath("create_dtime", ".//div[has-class('author')]//div[has-class('date')]/text()")

            yield loader.load_item()

        next_page = response.xpath("//a[@data-container-id='infinite-list']/@data-url").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_reviews)
