import json
import re
from typing import Optional
from urllib.parse import unquote, urljoin

import dateparser


def normalize_space(string: str) -> str:
    """
    Replaces sequences of whitespace characters by a single space,
    strips leading and trailing white-space from a string,
    and returns the resulting string.
    """
    return re.sub(r'\s+', ' ', string).strip()


def drop_blank(string: str) -> Optional[str]:
    return string if string else None


def format_date(date: str) -> Optional[str]:
    """
    Format date string to ISO, return `None` on failure.
    """
    settings = {'TIMEZONE': 'Europe/Moscow', 'RETURN_AS_TIMEZONE_AWARE': True}
    date = dateparser.parse(normalize_space(date), settings=settings)
    return None if date is None else date.isoformat()


def format_url(url: str, loader_context: dict) -> Optional[str]:
    if loader_context.get('response'):
        base = loader_context['response'].url
    elif loader_context.get('url'):
        base = loader_context['url']
    else:
        return None
    return unquote(urljoin(base, url))


class StartUrlsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'start_urls', None) and isinstance(self.start_urls, str):
            self.start_urls = json.loads(self.start_urls)
