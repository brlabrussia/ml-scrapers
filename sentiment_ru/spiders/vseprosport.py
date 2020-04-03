import scrapy
import w3lib.url
from scrapy.http import Response

from sentiment_ru.items import ReviewLoader


class VseprosportSpider(scrapy.Spider):
    name = "vseprosport"
    allowed_domains = ["vseprosport.ru"]
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://www.vseprosport.ru/reyting-bukmekerov/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response: Response):
        xp = "//div[has-class('bookmeker_table_offer')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_url = "https://www.vseprosport.ru"
            bookmaker_url += bookmaker_block.xpath(".//div[has-class('bookmeker_table_offer_button')]//a/@href").get()
            bookmaker_id = bookmaker_url.split("/")[-1]
            bookmaker_name = bookmaker_block.xpath(".//div[has-class('bookmeker_table_offer_logo')]//img/@title").get()

            params = {
                "book": bookmaker_id,
                "offsetNews": 0,
            }
            url = "https://www.vseprosport.ru/get-bookmaker-comments-html"
            url = w3lib.url.add_or_replace_parameters(url, params)
            cb_kwargs = {"bookmaker_name": bookmaker_name, "bookmaker_url": bookmaker_url}
            yield response.follow(url, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response: Response, bookmaker_name: str, bookmaker_url: str):
        xp = "//body/li"
        review_blocks = response.xpath(xp)
        if not review_blocks:
            return
        for review_block in review_blocks:
            loader = ReviewLoader(selector=review_block)
            loader.add_xpath("author", "./figure//h4/text()")
            loader.add_xpath("content", "./p[has-class('message')]/text()")
            loader.add_xpath("rating", "./figure//div[has-class('star-rate')]/ul/b/text()", re=r"^(\d+)")
            loader.add_value("rating_max", 5)
            loader.add_value("rating_min", 1)
            loader.add_value("subject", bookmaker_name)
            loader.add_xpath("time", ".//p[has-class('date')]/text()")
            loader.add_value("type", "review")
            loader.add_value("url", bookmaker_url)
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            url = response.request.url
            offset = int(w3lib.url.url_query_parameter(url, "offsetNews"))
            next_offset = offset + 5
            url = w3lib.url.add_or_replace_parameter(url, "offsetNews", next_offset)
            cb_kwargs = {"bookmaker_name": bookmaker_name}
            yield response.follow(url, cb_kwargs=cb_kwargs, callback=self.parse_reviews)
