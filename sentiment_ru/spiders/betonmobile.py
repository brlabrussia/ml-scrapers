import scrapy
from scrapy.http import Response

from sentiment_ru.items import ReviewLoader


class BetonmobileSpider(scrapy.Spider):
    name = "betonmobile"
    allowed_domains = ["betonmobile.ru"]
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://betonmobile.ru/vse-bukmekerskie-kontory"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response: Response):
        xp = "//td[has-class('td-view')]/a/@href"
        bookmaker_links = response.xpath(xp)
        for bookmaker_link in bookmaker_links:
            yield response.follow(bookmaker_link, callback=self.parse_bookmaker_info)

    def parse_bookmaker_info(self, response: Response):
        bookmaker_id = response.xpath("//link[@rel='shortlink']/@href").get()
        bookmaker_id = bookmaker_id.split("?p=")[-1]
        bookmaker_name = response.xpath("//h1[has-class('section-title')]/text()").get()

        url = "https://betonmobile.ru/wp-admin/admin-ajax.php"
        formdata = {
            "action": "cloadmore",
            "post_id": bookmaker_id,
            "cpage": "1",
        }
        cb_kwargs = {
            "formdata": formdata,
            "bookmaker_name": bookmaker_name,
        }
        yield scrapy.FormRequest(url, formdata=formdata, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response: Response, formdata: dict, bookmaker_name: str):
        xp = "//body/li/div[has-class('comment')]"
        review_blocks = response.xpath(xp)
        if not review_blocks:
            return
        for review_block in review_blocks:
            loader = ReviewLoader(selector=review_block)
            loader.add_xpath("author", ".//div[has-class('comhed')]/p[has-class('comaut')]/text()")
            loader.add_xpath("content", "./div[has-class('comment-content')]/p/text()")
            loader.add_value("subject", bookmaker_name)
            loader.add_xpath("time", "./div[has-class('comment-meta')]//time[@datetime]/@datetime")
            loader.add_value("type", "review")
            loader.add_value("url", response.request.url)
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            url = response.request.url
            page = int(formdata["cpage"])
            page += 1
            formdata["cpage"] = str(page)
            cb_kwargs = {
                "formdata": formdata,
                "bookmaker_name": bookmaker_name,
            }
            yield scrapy.FormRequest(url, formdata=formdata, cb_kwargs=cb_kwargs, callback=self.parse_reviews)