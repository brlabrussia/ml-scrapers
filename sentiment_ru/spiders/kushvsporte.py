import json

import scrapy
from scrapy.http import Response

from sentiment_ru.items import ReviewLoader


class KushvsporteSpider(scrapy.Spider):
    name = "kushvsporte"
    allowed_domains = ["kushvsporte.ru"]
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://kushvsporte.ru/bookmaker/rating"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response: Response):
        xp = "//div[has-class('blockBkList')]/*"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_name = bookmaker_block.xpath(".//h3/text()").get()
            bookmaker_link = bookmaker_block.xpath(".//a[@class='medium']/@href").get()
            cb_kwargs = {"bookmaker_name": bookmaker_name}
            yield response.follow(bookmaker_link, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response: Response, bookmaker_name: str):
        xp = "//*[@id='reviews-block']/div[has-class('review')]"
        review_blocks = response.xpath(xp)
        for review_block in review_blocks:
            loader = ReviewLoader(selector=review_block)
            loader.add_xpath("author", ".//div[has-class('infoUserRevievBK')]/*[@itemprop='name']/@title")
            loader.add_xpath("content_positive", ".//div[@itemprop='reviewBody']//p[1]/text()")
            loader.add_xpath("content_negative", ".//div[@itemprop='reviewBody']//p[2]/text()")
            loader.add_xpath("content_comment", ".//div[@itemprop='reviewBody']//p[3]/text()")
            loader.add_xpath("rating", ".//meta[@itemprop='ratingValue']/@content")
            loader.add_value("rating_max", 5)
            loader.add_value("rating_min", 1)
            loader.add_value("subject", bookmaker_name)
            loader.add_xpath("time", ".//meta[@itemprop='datePublished']/@datetime")
            loader.add_value("type", "review")
            loader.add_value("url", response.request.url)
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            xp = "//a[@id='list-reviews-pagination'][@data-urls!='[]']/@data-urls"
            next_page = response.xpath(xp).get()
            if next_page:
                next_page = json.loads(next_page)[0]
                cb_kwargs = {"bookmaker_name": bookmaker_name}
                yield response.follow(next_page, cb_kwargs=cb_kwargs, callback=self.parse_reviews)
