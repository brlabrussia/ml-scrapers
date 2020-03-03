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
            content = ""
            content += self.format_value(item.get("title"), "Заголовок")
            content += self.format_value(item.get("pluses"), "Плюсы")
            content += self.format_value(item.get("minuses"), "Минусы")
            content += self.format_value(item.get("comment"), "Комментарий")
            content = content.strip()
            if not content:
                raise DropItem(f"Can't build content for {item}")
            item["content"] = content
        return item

    @staticmethod
    def format_value(value, name):
        return f'"{name}": {value}\n\n' if value else ""
