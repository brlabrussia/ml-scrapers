import logging
import re

from premailer import transform
from scrapy.loader.processors import Compose
from scrapy.selector import Selector, SelectorList


def remove_style_tags(string: str) -> str:
    return re.sub(r'<style.*?</style>', r'', string, flags=re.S)


def remove_unwanted_attributes(string: str) -> str:
    return re.sub(r'\s(?!style|src|alt|height|width|rowspan|colspan|text-align)[\w-]+="[^"]*?"', r'', string, flags=re.S)


def normalize_style_attributes(string: str) -> str:
    return re.sub(r'(style="[^"]+)"', r'\1;"', string, flags=re.S)


def remove_browser_css_properties(string: str) -> str:
    return re.sub(r'-(?:o|ms|moz|webkit)-.*?;\s?', r'', string, flags=re.S)


def remove_weird_css_properties(string: str) -> str:
    return re.sub(r'(?:animation|transition|transform)[^;"]+?;\s?', r'', string, flags=re.S)


def remove_color_css_properties(string: str) -> str:
    return re.sub(r'(?:[\w\-]+?)?color[^;"]+;\s?', r'', string, flags=re.S)


def replace_anchors(string: str) -> str:
    return re.sub(r'<a\b(.*?>)', r'<span\1', string, flags=re.S)


BASIC_POST_PROCESSOR = Compose(
    remove_style_tags,
    remove_unwanted_attributes,
    normalize_style_attributes,
    remove_browser_css_properties,
    remove_weird_css_properties,
    remove_color_css_properties,
    replace_anchors,
)


def prepare_table_selector(
    table_selector: SelectorList,
    response,
    stylesheets=None,
    styletags=None,
    post_processor=None,
):
    if stylesheets is None:
        stylesheets = response.css('link[rel=stylesheet]::attr(href)').getall()
    elif isinstance(stylesheets, str):
        stylesheets = response.css(stylesheets).getall()

    if styletags is None:
        styletags = response.css('style::text').getall()
    elif isinstance(styletags, str):
        styletags = response.css(styletags).getall()

    if post_processor is None:
        post_processor = BASIC_POST_PROCESSOR

    html = transform(
        html=table_selector.get(),
        base_url=response.url,
        external_styles=stylesheets,
        css_text=styletags,
        disable_validation=True,
        cssutils_logging_level=logging.CRITICAL,
    )
    html = post_processor(html)

    return Selector(text=html)
