from scrapy.exceptions import DropItem


class BuildContentPipeline(object):
    """
    Try to build `content` field from secondary fields: (`title`, `comment`,
    `pluses` and `minuses`), pop them in the process.
    Drop item on failure.
    """

    def process_item(self, item, spider):
        def decorate_value(value, prefix):
            return f'"{prefix}": {value}\n\n' if value else ""

        if not item.get("content"):
            value_prefix_pairs = [
                (item.pop("title", None), "Заголовок"),
                (item.pop("pluses", None), "Плюсы"),
                (item.pop("minuses", None), "Минусы"),
                (item.pop("comment", None), "Комментарий"),
            ]
            content = "".join(decorate_value(v, p) for v, p in value_prefix_pairs)
            content = content.strip()
            if not content:
                raise DropItem(f"Can't build content for {item}")
            item["content"] = content
        return item
