import scrapy

from scrapy_project.items import ReviewLoader


# TODO: bookmaker name formatting, remove intermediate bookmaker name and id parsing
class BetonmobileSpider(scrapy.Spider):
    name = "betonmobile"
    source_name = "Betonmobile"
    allowed_domains = ["betonmobile.ru"]

    def start_requests(self):
        url = "https://betonmobile.ru/vse-bukmekerskie-kontory"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//td[has-class('td-view')]/a/@href"
        bookmaker_links = response.xpath(xp)
        for bookmaker_link in bookmaker_links:
            yield response.follow(bookmaker_link, callback=self.parse_bookmaker_info)

    def parse_bookmaker_info(self, response):
        bookmaker_name = response.xpath("//h1[has-class('section-title')]/text()").get()
        bookmaker_id = response.xpath("//link[@rel='shortlink']/@href").get()
        bookmaker_id = bookmaker_id.split("?p=")[-1]
        formdata = {
            "action": "cloadmore",
            "post_id": bookmaker_id,
            "cpage": "1",
        }
        url = "https://betonmobile.ru/wp-admin/admin-ajax.php"
        cb_kwargs = {"bookmaker_name": bookmaker_name, "formdata": formdata}
        yield scrapy.FormRequest(url, formdata=formdata, callback=self.parse_reviews, cb_kwargs=cb_kwargs)

    def parse_reviews(self, response, bookmaker_name, formdata):
        xp = "//body/li/div[has-class('comment')]"
        reviews = response.xpath(xp)
        if not reviews:
            return
        for review in reviews:
            loader = ReviewLoader(selector=review)
            loader.add_value("source", self.source_name)
            loader.add_value("bookmaker", bookmaker_name)
            loader.add_xpath("username", ".//div[has-class('comhed')]/p[has-class('comaut')]/text()")
            loader.add_xpath("create_dtime", "./div[has-class('comment-meta')]//time[@datetime]/@datetime")
            loader.add_xpath("content", "./div[has-class('comment-content')]/p/text()")
            yield loader.load_item()

        url = response.request.url
        page = int(formdata["cpage"])
        page += 1
        formdata["cpage"] = str(page)
        cb_kwargs = {"bookmaker_name": bookmaker_name, "formdata": formdata}
        yield scrapy.FormRequest(url, formdata=formdata, callback=self.parse_reviews, cb_kwargs=cb_kwargs)
