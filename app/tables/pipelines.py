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
