import scrapy
import w3lib.url

from scrapy_project.items import ReviewLoader


# TODO: make sure every single review is scraped
class VseprosportSpider(scrapy.Spider):
    name = "vseprosport"
    source_name = "ВсеПроСпорт.ру"
    allowed_domains = ["vseprosport.ru"]

    def start_requests(self):
        url = "https://www.vseprosport.ru/reyting-bukmekerov/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//div[has-class('bookmeker_table_offer')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_name = bookmaker_block.xpath(".//div[has-class('bookmeker_table_offer_logo')]//img/@title").get()
            bookmaker_link = bookmaker_block.xpath(".//div[has-class('bookmeker_table_offer_button')]//a/@href").get()
            bookmaker_id = bookmaker_link.split("/")[-1]
            params = {
                "book": bookmaker_id,
                "offsetNews": 0,
            }
            url = "https://www.vseprosport.ru/get-bookmaker-comments-html"
            url = w3lib.url.add_or_replace_parameters(url, params)
            cb_kwargs = {"bookmaker_name": bookmaker_name}
            yield response.follow(url, callback=self.parse_reviews, cb_kwargs=cb_kwargs)

    def parse_reviews(self, response, bookmaker_name):
        xp = "//body/li"
        reviews = response.xpath(xp)
        if not reviews:
            return
        for review in reviews:
            loader = ReviewLoader(selector=review)

            loader.add_value("bookmaker", bookmaker_name)
            loader.add_value("source", self.source_name)

            loader.add_xpath("content", "./p[has-class('message')]/text()")
            loader.add_value("title", "")
            loader.add_value("comment", "")
            loader.add_value("pluses", "")
            loader.add_value("minuses", "")

            loader.add_xpath("rating", "./figure//div[has-class('star-rate')]/ul/b/text()", re=r"^(\d+)")
            loader.add_xpath("username", "./figure//h4/text()")
            loader.add_xpath("create_dtime", ".//p[has-class('date')]/text()")

            yield loader.load_item()

        # Prepare url for page with next 5 reviews (offsetNews += 5)
        url = response.request.url
        offset = int(w3lib.url.url_query_parameter(url, "offsetNews"))
        next_offset = offset + 5
        url = w3lib.url.add_or_replace_parameter(url, "offsetNews", next_offset)
        cb_kwargs = {"bookmaker_name": bookmaker_name}
        yield response.follow(url, callback=self.parse_reviews, cb_kwargs=cb_kwargs)
