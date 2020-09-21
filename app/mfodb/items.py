import re
from typing import Optional
from urllib.parse import unquote

import dateparser
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity, MapCompose, TakeFirst


def normalize_space(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    if text:
        return text


def format_date(date: str) -> Optional[str]:
    """
    Take any scraped date and format it to ISO, return `None` on failure.
    """
    settings = {'TIMEZONE': 'Europe/Moscow', 'RETURN_AS_TIMEZONE_AWARE': True}
    date = dateparser.parse(date, settings=settings)
    if date is None:
        return None
    date = date.isoformat()
    return date


class Lender(Item):
    scraped_from = Field()

    trademark = Field(help_text='Торговая марка')
    name_short = Field(help_text='Сокращенное наименование')
    name_full = Field(help_text='Полное наименование')
    logo_origin_url = Field(help_text='Логотип')
    documents = Field(help_text='Документы')

    is_legal = Field(help_text='Легальная МФО (есть в реестре ЦБ)')
    cbr_created_at = Field(help_text='Дата внесения в реестр ЦБ')
    type = Field(help_text='Вид МФО')
    cbrn = Field(help_text='Регномер в ЦБ')
    ogrn = Field(help_text='ОГРН')
    inn = Field(help_text='ИНН')

    website = Field(help_text='Вебсайт')
    email = Field(help_text='Электронная почта')
    socials = Field(help_text='Соцсети')
    address = Field(help_text='Адрес')
    head_name = Field(help_text='Руководитель')

    decision_speed = Field(help_text='Скорость рассмотрения заявки')
    payment_speed = Field(help_text='Скорость выплаты')
    amount_min = Field(help_text='Минимальная сумма займа')
    amount_max = Field(help_text='Максимальная сумма займа')
    overpayment_day = Field(help_text='Переплата за день')
    overpayment_full = Field(help_text='Переплата за весь срок')
    decline_reasons = Field(help_text='Причины отказа')


class Loan(Item):
    # * О займе
    # https://www.banki.ru/microloans/products/2/
    name = Field(help_text='Название займа')
    banki_url = Field(help_text='Ссылка на Банки.ру')
    banki_updated_at = Field(help_text='Дата актуализации на Банки.ру')
    # ** Условия и ставки
    purposes = Field(help_text='Цель займа')
    amount_min = Field(help_text='Минимальная сумма займа')
    amount_max = Field(help_text='Максимальная сумма займа')
    amount_note = Field(help_text='Допинфа по сумме займа')
    rate_min = Field(help_text='Минимальная ставка в день')
    rate_max = Field(help_text='Максимальная ставка в день')
    rate_note = Field(help_text='Допинфа по ставке')
    period_min = Field(help_text='Минимальный срок займа')
    period_max = Field(help_text='Максимальный срок займа')
    period_note = Field(help_text='Допинфа по срокам')
    collateral = Field(help_text='Обеспечение')
    # ** Требования и документы
    borrower_categories = Field(help_text='Категории заемщиков')
    borrower_age = Field(help_text='Возраст заемщика')
    borrower_registration = Field(help_text='Регистрация заемщика')
    borrower_documents = Field(help_text='Документы заемщика')
    # ** Выдача
    application_process = Field(help_text='Оформление займа')
    payment_speed = Field(help_text='Срок выдачи')
    payment_forms = Field(help_text='Форма выдачи')
    payment_forms_note = Field(help_text='Допинфа по форме выдачи')
    # ** Погашение
    repayment_process = Field(help_text='Порядок погашения')
    repayment_process_note = Field(help_text='Допинфа по порядку погашения')
    repayment_forms = Field(help_text='Способ оплаты')

    # * Об организации
    lender_logo = Field(help_text='Логотип организации')
    lender_trademark = Field(help_text='Торговая марка')
    lender_address = Field(help_text='Адрес')
    lender_head_name = Field(help_text='Руководитель')
    lender_cbrn = Field(help_text='Регномер в ЦБ')
    lender_ogrn = Field(help_text='ОГРН')


class BasicLoader(ItemLoader):
    default_item_class = Lender
    default_input_processor = MapCompose(normalize_space)
    default_output_processor = TakeFirst()

    scraped_from_out = Identity()
    cbr_created_at_in = MapCompose(
        normalize_space,
        format_date,
    )


class CbrLoader(BasicLoader):
    website_in = MapCompose(
        str.lower,
        normalize_space,
        lambda x: x.replace(', ', ';'),
        lambda x: x.split(';')[0],
        lambda x: x.split(' ')[0],
        lambda x: x if x.startswith('http') else 'http://' + x,
    )
    email_in = MapCompose(
        str.lower,
        normalize_space,
        lambda x: x.replace(', ', ';'),
        lambda x: x.split(';')[0],
        lambda x: x.split(' ')[0],
    )


class ZaymovLoader(BasicLoader):
    pass


class VsezaimyonlineLoader(BasicLoader):
    logo_origin_url_in = MapCompose(
        normalize_space,
        lambda x: ('https://vsezaimyonline.ru' + x) if x.startswith('/') else x,
    )
    decline_reasons_out = Identity()
    socials_in = MapCompose(
        unquote,
        lambda x: x if x.startswith('http') else None,
    )
    socials_out = Compose(set)
    documents_in = Identity()
    documents_out = Identity()


class BankiLoader(BasicLoader):
    default_item_class = Loan

    banki_updated_at_in = MapCompose(format_date)
    purposes_out = Identity()
    amount_min_in = amount_max_in = MapCompose(
        str.lower,
        normalize_space,
        lambda x: x.replace(' ', ''),
        int,
    )
    rate_min_in = rate_max_in = MapCompose(
        str.lower,
        normalize_space,
        lambda x: x.replace(',', '.'),
        float,
    )
    period_min_in = period_max_in = MapCompose(int)
    collateral_out = Identity()
    borrower_categories_out = Identity()
    borrower_registration_out = Identity()
    borrower_documents_out = Identity()
    application_process_out = Identity()
    payment_forms_out = Identity()
    repayment_process_out = Identity()
    repayment_forms_out = Identity()

    lender_logo_in = MapCompose(
        normalize_space,
        lambda x: ('http:' + x) if x.startswith('//') else x,
    )
    lender_address_in = MapCompose(
        normalize_space,
        lambda x: re.sub(r'<.*?>', '', x),
    )
