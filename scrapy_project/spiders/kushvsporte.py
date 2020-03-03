import json

import scrapy
from scrapy.loader import ItemLoader

from scrapy_project.items import ReviewLoader


class KushvsporteSpider(scrapy.Spider):
    name = "kushvsporte"
    source_name = "Kush v sporte"
    allowed_domains = ["kushvsporte.ru"]

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
            yield response.follow(bookmaker_link, callback=self.parse_reviews, cb_kwargs=cb_kwargs)

    def parse_reviews(self, response, bookmaker_name):
        xp = "//*[@id='reviews-block']/div[has-class('review')]"
        reviews = response.xpath(xp)
        for review in reviews:
            loader = ReviewLoader(selector=review)

            # TODO: format date
            loader.add_value("bookmaker", bookmaker_name)
            loader.add_value("source", self.source_name)

            loader.add_value("content", "")
            loader.add_value("title", "")
            loader.add_xpath("comment", ".//div[@itemprop='reviewBody']//p[3]/text()")
            loader.add_xpath("pluses", ".//div[@itemprop='reviewBody']//p[1]/text()")
            loader.add_xpath("minuses", ".//div[@itemprop='reviewBody']//p[2]/text()")

            loader.add_xpath("rating", ".//meta[@itemprop='ratingValue']/@content")
            loader.add_xpath("username", ".//div[has-class('infoUserRevievBK')]/*[@itemprop='name']/@title")
            loader.add_xpath("create_dtime", ".//meta[@itemprop='datePublished']/@datetime")

            yield loader.load_item()

        xp = "//a[@id='list-reviews-pagination'][@data-urls!='[]']/@data-urls"
        next_page = response.xpath(xp).get()
        if next_page:
            next_page = json.loads(next_page)[0]
            cb_kwargs = {"bookmaker_name": bookmaker_name}
            yield response.follow(next_page, callback=self.parse_reviews, cb_kwargs=cb_kwargs)
