import dateparser
from scrapy.exceptions import DropItem


class BuildContentPipeline(object):
    def process_item(self, item, spider):
        if not item.get("content"):
            content = ""
            content += self.format_value(item.pop("title", None), "Заголовок")
            content += self.format_value(item.pop("pluses", None), "Плюсы")
            content += self.format_value(item.pop("minuses", None), "Минусы")
            content += self.format_value(item.pop("comment", None), "Комментарий")
            content = content.strip()
            if not content:
                raise DropItem(f"Can't build content for {item}")
            item["content"] = content
        return item

    @staticmethod
    def format_value(value, name):
        return f'"{name}": {value}\n\n' if value else ""
