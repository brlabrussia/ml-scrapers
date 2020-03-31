import json

import scrapy

from sentiment_ru.items import ReviewLoader


class KushvsporteSpider(scrapy.Spider):
    name = "kushvsporte"
    source_name = "Kush v sporte"
    allowed_domains = ["kushvsporte.ru"]
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://kushvsporte.ru/bookmaker/rating"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//div[has-class('blockBkList')]/*"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_name = bookmaker_block.xpath(".//h3/text()").get()
            bookmaker_link = bookmaker_block.xpath(".//a[@class='medium']/@href").get()
            cb_kwargs = {"bookmaker_name": bookmaker_name}
            yield response.follow(bookmaker_link, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response, bookmaker_name):
        xp = "//*[@id='reviews-block']/div[has-class('review')]"
        review_blocks = response.xpath(xp)
        for review_block in review_blocks:
            loader = ReviewLoader(selector=review_block)
            loader.add_value("source", self.source_name)
            loader.add_value("bookmaker", bookmaker_name)
            loader.add_xpath("rating", ".//meta[@itemprop='ratingValue']/@content")
            loader.add_xpath("username", ".//div[has-class('infoUserRevievBK')]/*[@itemprop='name']/@title")
            loader.add_xpath("create_dtime", ".//meta[@itemprop='datePublished']/@datetime")
            loader.add_xpath("pluses", ".//div[@itemprop='reviewBody']//p[1]/text()")
            loader.add_xpath("minuses", ".//div[@itemprop='reviewBody']//p[2]/text()")
            loader.add_xpath("comment", ".//div[@itemprop='reviewBody']//p[3]/text()")
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            xp = "//a[@id='list-reviews-pagination'][@data-urls!='[]']/@data-urls"
            next_page = response.xpath(xp).get()
            if next_page:
                next_page = json.loads(next_page)[0]
                cb_kwargs = {"bookmaker_name": bookmaker_name}
                yield response.follow(next_page, cb_kwargs=cb_kwargs, callback=self.parse_reviews)
