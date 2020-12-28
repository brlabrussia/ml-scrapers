import os

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
            spider.logger.info('process_item')
        return item

    def process_wikipedia(self, item, spider):
        body = item['body']
        if 'Чемпион</b>' in body[0][0]['value']:
            spider.logger.info('champ')
            body.pop(0)
            if not body[0][0]['value']:
                body[0][0]['value'] = '<b>Ч</b>'
                body[0][1]['value'] = f'<b>{body[0][1]["value"]}</b>'
                body[0][2]['value'] = f'<b>{body[0][2]["value"]}</b>'
            if not body[1][0]['value'] and body[1][0]['colspan'] == '3':
                body.pop(1)
        item['body'] = body
        return item
