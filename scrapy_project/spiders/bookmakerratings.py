import scrapy

from scrapy_project.items import ReviewLoader


class BookmakerratingsSpider(scrapy.Spider):
    name = "bookmakerratings"
    source_name = "Рейтинг Букмекеров"
    allowed_domains = ["bookmaker-ratings.ru"]
    custom_settings = {"CONCURRENT_REQUESTS": 4}

    def start_requests(self):
        url = "https://bookmaker-ratings.ru/bookmakers-homepage/vse-bukmekerskie-kontory/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//div[has-class('table-container')]/div[has-class('table-row')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_id = bookmaker_block.xpath("./@data-id").get()
            bookmaker_name = bookmaker_block.xpath("./@data-name").get()
            formdata = {
                "action": "feedbacks_items_page",
                "page": "1",
                "postID": bookmaker_id,
            }
            url = "https://bookmaker-ratings.ru/wp-admin/admin-ajax.php"
            cb_kwargs = {"bookmaker_name": bookmaker_name, "formdata": formdata}
            yield scrapy.FormRequest(url, formdata=formdata, callback=self.parse_reviews, cb_kwargs=cb_kwargs)

    def parse_reviews(self, response, bookmaker_name, formdata):
        xp = "//body/div[has-class('single')]"
        reviews = response.xpath(xp)
        if not reviews:
            return
        for review in reviews:
            loader = ReviewLoader(selector=review)
            loader.add_value("source", self.source_name)
            loader.add_value("bookmaker", bookmaker_name)
            loader.add_xpath("rating", ".//span[has-class('feedbacks-rating-stars')]/span[has-class('num')]/text()")
            loader.add_xpath("username", ".//a[has-class('namelink')]/text()")
            loader.add_value("username", "account is deleted")
            loader.add_xpath("create_dtime", ".//div[has-class('date')]/text()")
            loader.add_xpath("content", ".//div[has-class('content')]/div[has-class('text')]/*/text()")
            yield loader.load_item()

        url = response.request.url
        page = int(formdata["page"])
        page += 1
        formdata["page"] = str(page)
        cb_kwargs = {"bookmaker_name": bookmaker_name, "formdata": formdata}
        yield scrapy.FormRequest(url, formdata=formdata, callback=self.parse_reviews, cb_kwargs=cb_kwargs)
