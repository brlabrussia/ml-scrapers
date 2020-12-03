import json


class StartUrlsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'start_urls', None) and isinstance(self.start_urls, str):
            self.start_urls = json.loads(self.start_urls)
