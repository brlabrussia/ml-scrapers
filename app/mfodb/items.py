import re

import dateparser
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst


def normalize_space(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    if text:
        return text


def format_date(date):
    """
    Take any scraped date and format it to ISO, return `None` on failure.
    """
    settings = {'TIMEZONE': 'Europe/Moscow', 'RETURN_AS_TIMEZONE_AWARE': True}
    date = dateparser.parse(date, settings=settings)
    if date is None:
        return None
    date = date.isoformat()
    return date


class BankiItem(Item):
    address = Field()
    borrowers_age = Field()
    borrowers_categories = Field()
    borrowers_documents = Field()
    borrowers_registration = Field()
    dates_from = Field()
    dates_to = Field()
    first_loan_condition = Field()
    head_name = Field()
    issuance = Field()
    loan_form = Field()
    loan_form_description = Field()
    loan_processing = Field()
    loan_providing = Field()
    loan_purpose = Field()
    loan_time_terms = Field()
    logo = Field()
    max_money_value = Field()
    name = Field()
    ogrn = Field()
    payment_methods = Field()
    rate = Field()
    reg_number = Field()
    repayment_order = Field()
    repayment_order_description = Field()
    trademark = Field()
    updated_at = Field()
    url = Field()
    website = Field()


class BankiLoader(ItemLoader):
    default_item_class = BankiItem
    default_input_processor = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    logo_in = MapCompose(
        normalize_space,
        lambda x: ('http:' + x) if x.startswith('//') else x,
    )
    updated_at_in = MapCompose(format_date)
    loan_purpose_out = Identity()
    max_money_value_in = MapCompose(
        lambda x: x.replace(' ', ''),
        int,
    )
    # rate_in = MapCompose(
    #     lambda x: x.replace(',', '.'),
    #     float,
    # )
    dates_from_in = MapCompose(int)
    dates_to_in = MapCompose(int)
    loan_providing_out = Identity()
    borrowers_categories_out = Identity()
    borrowers_registration_out = Identity()
    borrowers_documents_out = Identity()
    loan_processing_out = Identity()
    loan_form_out = Identity()
    repayment_order_out = Identity()
    payment_methods_out = Identity()
    address_in = MapCompose(
        normalize_space,
        lambda x: re.sub(r'<.*?>', '', x),
    )
    ogrn_in = MapCompose(int)
    reg_number_in = MapCompose(int)


class CbrItem(Item):
    address = Field()
    email = Field()
    full_name = Field()
    inn = Field()
    mfo_type = Field()
    name = Field()
    ogrn = Field()
    reg_number = Field()
    registry_date = Field()
    url = Field()


class CbrLoader(ItemLoader):
    default_item_class = CbrItem
    default_input_processor = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    reg_number_in = MapCompose(int)
    registry_date_in = MapCompose(format_date)
    ogrn_in = MapCompose(int)
    inn_in = MapCompose(int)


class VsezaimyonlineItem(Item):
    documents = Field()
    inn = Field()
    logo = Field()
    name = Field()
    ogrn = Field()
    refusal_reasons = Field()
    social_networks = Field()
    url = Field()


class VsezaimyonlineLoader(ItemLoader):
    default_item_class = VsezaimyonlineItem
    default_input_processor = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    logo_in = MapCompose(
        normalize_space,
        lambda x: ('https://vsezaimyonline.ru' + x) if x.startswith('/') else x,
    )
    ogrn_in = MapCompose(int)
    inn_in = MapCompose(int)
    refusal_reasons_out = Identity()
    social_networks_out = Identity()
    documents_in = Identity()
    documents_out = Identity()


class ZaymovItem(Item):
    address = Field()
    logo = Field()
    name = Field()
    ogrn = Field()
    reg_number = Field()
    registry_date = Field()
    url = Field()
    website = Field()


class ZaymovLoader(ItemLoader):
    default_item_class = ZaymovItem
    default_input_processor = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    reg_number_in = MapCompose(int)
    ogrn_in = MapCompose(int)
    registry_date_in = MapCompose(format_date)
