from scrapy.exceptions import DropItem


class NormalizeValuesPipeline(object):
    def process_item(self, item, spider):
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = value.strip()
        return item


class BuildContentPipeline(object):
    def process_item(self, item, spider):
        if not item.get("content"):
            title = item.get("title")
            title_term = f'"Заголовок": {title}' if title else ""
            pluses = item.get("pluses")
            pluses_term = f'"Плюсы": {pluses}' if pluses else ""
            minuses = item.get("minuses")
            minuses_term = f'"Минусы": {minuses}' if minuses else ""
            comment = item.get("comment")
            comment_term = f'"Комментарий": {comment}' if comment else ""
            content = title_term + "\n\n" + pluses_term + "\n\n" + minuses_term + "\n\n" + comment_term
            content = content.strip()
            if not content:
                raise DropItem(f"Can't build content for {item}")
            item["content"] = content
        return item
