import hashlib
import json

import psycopg2
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
                raise DropItem("Can't build content")
            item["content"] = content
        return item


class PostgresPipeline(object):
    """
    Exports items to database `scrapy`, table `<spider-name>`,
    schema `id CHAR (32) PRIMARY KEY, item JSON`.
    Checks if item is already in said table.
    """

    def open_spider(self, spider):
        # Basic setup and creation of table if it doesn't already exist
        self.connection = psycopg2.connect(host="postgres", user="postgres", password="postgres", dbname="scrapy")
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {spider.name} (id CHAR (32) PRIMARY KEY, item JSON);")
        self.connection.commit()

        # Get ids for items we already have, set() is used for performance reasons
        self.cursor.execute(f"SELECT id FROM {spider.name};")
        self.ids_seen = set(id_ for id_, *_ in self.cursor.fetchall())

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        # Bookmaker items
        if item.get("id") is not None:
            id_ = str(item.get("id"))
        # Review items
        elif item.get("content") is not None:
            id_ = item.get("bookmaker") + item.get("username") + item.get("content")
        id_ = hashlib.md5(id_.encode()).hexdigest()
        if id_ in self.ids_seen:
            raise DropItem("Already in database")
        else:
            item_ = json.dumps(dict(item))
            self.cursor.execute(f"INSERT INTO {spider.name} VALUES (%s, %s);", (id_, item_))
            self.connection.commit()
        return item
