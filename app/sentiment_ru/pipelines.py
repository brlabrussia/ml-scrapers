from scrapy.exceptions import DropItem


class BuildContentPipeline:
    """
    Try to build `content` field from secondary fields: (`content_title`,
    `content_positive`, `content_negative` and `content_comment`), ~~pop them
    in the process~~.

    Drop item on failure.
    """

    def process_item(self, item, spider):
        def decorate_value(value: str, prefix: str) -> str:
            return f'"{prefix}": {value}\n\n' if value else ''

        if not item.get('content'):
            value_prefix_pairs = [
                # TODO pop unnecessary fields
                (item.get('content_title', None), 'Заголовок'),
                (item.get('content_positive', None), 'Плюсы'),
                (item.get('content_negative', None), 'Минусы'),
                (item.get('content_comment', None), 'Комментарий'),
            ]
            content = ''.join(decorate_value(v, p) for v, p in value_prefix_pairs)
            content = content.strip()
            if not content:
                raise DropItem("Can't build content")
            item['content'] = content
        return item
