import scrapy

from sentiment_ru.items import ReviewLoader


class BookmakerratingsSpider(scrapy.Spider):
    name = "bookmakerratings"
    source_name = "Рейтинг Букмекеров"
    allowed_domains = ["bookmaker-ratings.ru"]
    custom_settings = {"CONCURRENT_REQUESTS": 4}  # avoid HTTP 429
    scrape_bookmaker_full = False  # whether to scrape all reviews for bookmaker

    def start_requests(self):
        url = "https://bookmaker-ratings.ru/bookmakers-homepage/vse-bukmekerskie-kontory/"
        yield scrapy.Request(url, callback=self.parse_bookmakers)

    def parse_bookmakers(self, response):
        xp = "//div[has-class('table-container')]/div[has-class('table-row')]"
        bookmaker_blocks = response.xpath(xp)
        for bookmaker_block in bookmaker_blocks:
            bookmaker_id = bookmaker_block.xpath("./@data-id").get()
            bookmaker_name = bookmaker_block.xpath("./@data-name").get()

            url = "https://bookmaker-ratings.ru/wp-admin/admin-ajax.php"
            formdata = {
                "action": "feedbacks_items_page",
                "page": "1",
                "postID": bookmaker_id,
            }
            cb_kwargs = {
                "formdata": formdata,
                "bookmaker_name": bookmaker_name,
            }
            yield scrapy.FormRequest(url, formdata=formdata, cb_kwargs=cb_kwargs, callback=self.parse_reviews)

    def parse_reviews(self, response, formdata, bookmaker_name):
        xp = "//body/div[has-class('single')]"
        review_blocks = response.xpath(xp)
        if not review_blocks:
            return
        for review_block in review_blocks:
            loader = ReviewLoader(selector=review_block)
            loader.add_value("source", self.source_name)
            loader.add_value("bookmaker", bookmaker_name)
            loader.add_xpath("rating", ".//span[has-class('feedbacks-rating-stars')]/span[has-class('num')]/text()")
            loader.add_xpath("username", ".//a[has-class('namelink')]/text()")
            loader.add_value("username", "account is deleted")
            loader.add_xpath("create_dtime", ".//div[has-class('date')]/text()")
            loader.add_xpath("content", ".//div[has-class('content')]/div[has-class('text')]/*/text()")
            yield loader.load_item()

        if self.scrape_bookmaker_full:
            url = response.request.url
            page = int(formdata["page"])
            page += 1
            formdata["page"] = str(page)
            cb_kwargs = {
                "formdata": formdata,
                "bookmaker_name": bookmaker_name,
            }
            yield scrapy.FormRequest(url, formdata=formdata, cb_kwargs=cb_kwargs, callback=self.parse_reviews)
