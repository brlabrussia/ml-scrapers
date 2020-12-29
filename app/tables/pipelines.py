import os
import re

from default.pipelines import WebhookPipeline as WebhookPipeline_


class WebhookPipeline(WebhookPipeline_):
    def send_items(self):
        j = {'result': self.items[0]}
        response = self.client.patch(
            self.endpoint,
            json=j,
            auth=(os.getenv('INFO_USERNAME'), os.getenv('INFO_PASSWORD')),
        )
        self.stats.inc_value('webhook/items_count')
        if response.ok:
            self.stats.inc_value('webhook/response_count')
        self.stats.inc_value(f'webhook/response_status_count/{response.status_code}')
        self.items.clear()


class WikipediaPipeline:
    def process_item(self, item, spider):
        if spider.name == 'wikipedia':
            item = self.process_wikipedia(item, spider)
        return item

    def process_wikipedia(self, item, spider):
        body = item['body']
        for index, row in enumerate(body):
            # sus row
            if len(row) == 1:
                # next row's 1st value is empty
                if not body[index + 1][0]['value']:
                    # assign current row's 1st value to next row's 1st value
                    t = row[0]['value']
                    t = re.sub(r'<.*?>', '', t)
                    t = ''.join(w[0] for w in t.upper().split())
                    t = f'<b>{t}</b>'
                    body[index + 1][0]['value'] = t
                    # make rest of the values bold
                    for index2, data in enumerate(body[index + 1]):
                        if index2 == 0:
                            continue
                        body[index + 1][index2]['value'] = f'<b>{data["value"]}</b>'
                body.pop(index)
        item['body'] = body
        return item
