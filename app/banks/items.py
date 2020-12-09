import re
from typing import List, Optional
from urllib.parse import unquote

import bleach
import dateparser
from scrapy.item import Field, Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (
    Compose,
    Identity,
    Join,
    MapCompose,
    TakeFirst,
)


def normalize_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def drop_blanks(text: str) -> Optional[str]:
    return text if text else None


def format_date(date: str) -> Optional[str]:
    """
    Take any scraped date and format it to ISO, return `None` on failure.
    """
    date = normalize_spaces(date)
    settings = {'TIMEZONE': 'Europe/Moscow', 'RETURN_AS_TIMEZONE_AWARE': True}
    date = dateparser.parse(date, settings=settings)
    if date is None:
        return None
    date = date.isoformat()
    return date


def format_bonuses(self, loader_result: List[str]) -> str:
    text = ' '.join(loader_result)
    text = re.sub(r'[\n\r\t]+', '\n', text)
    return text.strip().split('\n')


class Bank(Item):
    cbr_url = Field()
    banki_url = Field()

    full_name = Field()
    name = Field()
    reg_number = Field()
    registration_date = Field()
    ogrn = Field()
    ogrn_date = Field()
    bik = Field()
    statutory_address = Field()
    actual_address = Field()
    tel_number = Field()
    statutory_update = Field()
    authorized_capital = Field()
    authorized_capital_date = Field()
    license_info = Field()
    license_info_file = Field()
    deposit_insurance_system = Field()
    english_name = Field()

    bank_subsidiaries = Field()
    bank_agencies = Field()
    additional_offices = Field()
    operating_cash_desks = Field()
    operating_offices = Field()
    mobile_cash_desks = Field()

    info_sites = Field()
    cards = Field()
    subsidiaries = Field()
    agencies = Field()


class CbrBankLoader(ItemLoader):
    default_item_class = Bank
    default_input_processor = MapCompose(normalize_spaces)
    default_output_processor = TakeFirst()

    registration_date_in = MapCompose(format_date)
    ogrn_date_in = MapCompose(format_date)
    tel_number_in = MapCompose(
        normalize_spaces,
        lambda x: x.split(', '),
    )
    tel_number_out = Identity()
    statutory_update_in = MapCompose(format_date)
    authorized_capital_in = MapCompose(
        normalize_spaces,
        lambda x: x if not x else int(x.replace(' ', '')),
    )
    authorized_capital_date_in = MapCompose(format_date)
    license_info_in = MapCompose(
        normalize_spaces,
        lambda x: x if x else None,
    )
    license_info_out = Identity()
    license_info_file_in = MapCompose(
        normalize_spaces,
        lambda x: ('http://cbr.ru' + x) if x.startswith('/') else x,
    )
    deposit_insurance_system_in = MapCompose(
        normalize_spaces,
        lambda x: True if x == 'Да' else (False if x == 'Нет' else None),
    )

    bank_subsidiaries_out = Join(', ')
    bank_agencies_in = MapCompose(int)
    additional_offices_in = MapCompose(int)
    operating_cash_desks_in = MapCompose(int)
    operating_offices_in = MapCompose(int)
    mobile_cash_desks_in = MapCompose(int)

    info_sites_in = MapCompose(unquote)
    info_sites_out = Identity()
    cards_in = cards_out = Identity()
    subsidiaries_in = subsidiaries_out = Identity()
    agencies_in = agencies_out = Identity()


class BankiBankLoader(ItemLoader):
    default_item_class = Bank
    default_input_processor = MapCompose(normalize_spaces)
    default_output_processor = TakeFirst()


class DebitCard(Item):
    banki_url = Field()
    banki_bank_url = Field()

    name = Field()
    images = Field()
    summary = Field()

    borrower_age = Field()
    borrower_registration = Field()
    expert_positive = Field()
    expert_negative = Field()
    expert_restrictions = Field()

    debit_type = Field()
    technological_features = Field()
    debit_cashback = Field()
    debit_cashback_description = Field()
    debit_bonuses = Field()
    interest_accrual = Field()
    service_cost = Field()
    cash_withdrawal = Field()
    cash_pickup_point = Field()
    foreign_cash_withdrawal = Field()
    foreign_cash_pickup_point = Field()
    operations_limit = Field()
    additional_information = Field()
    updated_at = Field()


class CreditCard(Item):
    banki_url = Field()
    banki_bank_url = Field()

    name = Field()
    images = Field()
    summary = Field()

    borrower_age = Field()
    borrower_registration = Field()
    expert_positive = Field()
    expert_negative = Field()
    expert_restrictions = Field()

    credit_type = Field()
    technological_features = Field()
    credit_cashback = Field()
    credit_cashback_description = Field()
    credit_bonuses = Field()
    interest_accrual = Field()
    service_cost = Field()
    cash_withdrawal = Field()
    cash_pickup_point = Field()
    foreign_cash_withdrawal = Field()
    foreign_cash_pickup_point = Field()
    operations_limit = Field()
    additional_information = Field()
    updated_at = Field()

    borrower_income = Field()
    borrower_experience = Field()
    credit_limit = Field()
    credit_limit_description = Field()
    credit_period = Field()
    grace_period = Field()
    percentage_grace = Field()
    percentage_grace_description = Field()
    percentage_credit = Field()
    percentage_credit_description = Field()
    repayment = Field()
    repayment_description = Field()
    own_funds = Field()


class AutoCredit(Item):
    banki_url = Field()
    banki_bank_url = Field()

    name = Field()

    auto_seller = Field()
    auto_kind = Field()
    auto_type = Field()
    auto_age = Field()
    autocredit_min_time = Field()
    autocredit_max_time = Field()
    autocredit_currency = Field()
    autocredit_amount_min = Field()
    autocredit_amount_max = Field()
    autocredit_amount_description = Field()
    min_down_payment = Field()
    loan_rate_min = Field()
    loan_rate_max = Field()
    loan_rate_description = Field()
    autocredit_comission = Field()
    early_moratorium_repayment = Field()
    prepayment_penalty = Field()
    insurance_necessity = Field()
    borrowers_age = Field()
    borrowers_age_description = Field()
    income_proof = Field()
    registration_requirements = Field()
    last_work_experience = Field()
    full_work_experience = Field()
    additional_conditions = Field()
    updated_at = Field()

    has_repurchase = Field()


class AutoCreditLoader(ItemLoader):
    default_item_class = AutoCredit
    default_input_processor = MapCompose(normalize_spaces)
    default_output_processor = TakeFirst()

    banki_bank_url_in = MapCompose(
        lambda x: ('https://www.banki.ru' + x) if x.startswith('/') else x,
    )
    auto_seller_in = MapCompose(
        normalize_spaces,
        lambda x: x if x else None,
    )
    auto_seller_out = Identity()
    auto_kind_in = MapCompose(
        lambda x: x.split(';'),
        normalize_spaces,
        lambda x: x if x else None,
    )
    auto_kind_out = Identity()
    auto_type_in = MapCompose(
        normalize_spaces,
        lambda x: x if x else None,
    )
    auto_type_out = Identity()
    auto_age_in = MapCompose(
        lambda x: x.split(';'),
        normalize_spaces,
    )
    auto_age_out = Identity()
    autocredit_amount_min_in = MapCompose(
        normalize_spaces,
        # lambda x: x.replace('\xa0', ' '),
    )
    autocredit_amount_description_in = MapCompose(
        lambda x: x.split('<br>'),
        lambda x: bleach.clean(x, tags=[], strip=True),
        normalize_spaces,
        # lambda x: x.replace('\xa0', ' '),
    )
    autocredit_amount_description_out = Compose(
        lambda x: ' '.join(x[1:]) if len(x) > 1 else None,
    )
    min_down_payment_in = MapCompose(
        lambda x: x.replace(',', '.'),
        float,
    )
    loan_rate_min_in = loan_rate_max_in = MapCompose(
        lambda x: x.replace(',', '.'),
        float,
    )
    loan_rate_description_in = Compose(
        lambda x: normalize_spaces(x[-1]) if len(x) >= 2 else None,
    )
    insurance_necessity_in = MapCompose(
        normalize_spaces,
        lambda x: True if x == 'да' else False,
    )
    borrowers_age_description_in = MapCompose(
        lambda x: x.split('<br>'),
        lambda x: bleach.clean(x, tags=[], strip=True),
        normalize_spaces,
    )
    borrowers_age_description_out = Compose(
        lambda x: ' '.join(x[1:]) if len(x) > 1 else None,
    )
    income_proof_out = Identity()
    registration_requirements_in = MapCompose(
        normalize_spaces,
        lambda x: x if x else None,
    )
    registration_requirements_out = Identity()
    updated_at_in = MapCompose(format_date)

    has_repurchase_in = MapCompose(
        normalize_spaces,
        lambda x: True if x == 'да' else False,
    )


class ConsumerCredit(Item):
    banki_url = Field()
    banki_bank_url = Field()

    name_base = Field()
    name_full = Field()

    account_currency = Field()
    loan_purpose = Field()
    loan_purpose_description = Field()
    credit_fee = Field()
    credit_fee_description = Field()
    loan_security = Field()
    loan_security_description = Field()
    credit_insurance = Field()
    credit_insurance_description = Field()
    additional_information = Field()
    rates_table = Field()
    borrowers_category = Field()
    borrowers_age_men = Field()
    borrowers_age_women = Field()
    work_experience = Field()
    work_experience_description = Field()
    borrowers_registration = Field()
    borrowers_income_description = Field()
    borrowers_income_tip = Field()
    borrowers_income_documents = Field()
    borrowers_documents = Field()
    borrowers_documents_description = Field()
    application_consider_time = Field()
    application_consider_time_description = Field()
    credit_decision_time = Field()
    loan_processing_terms = Field()
    loan_delivery_order = Field()
    loan_delivery_order_description = Field()
    loan_delivery_type = Field()
    loan_delivery_type_description = Field()
    repayment_procedure = Field()
    repayment_procedure_description = Field()
    early_repayment_full = Field()
    early_repayment_partial = Field()
    obligations_violation = Field()
    payment_method = Field()
    updated_at = Field()


class Deposit(Item):
    banki_url = Field()
    banki_bank_url = Field()

    name_base = Field()
    name_full = Field()

    deposit_amount = Field()
    deposit_currency = Field()
    deposit_term = Field()

    interest_payment = Field()
    interest_payment_description = Field()
    capitalization = Field()
    special_contribution = Field()
    special_contribution_description = Field()
    is_staircase_contribution = Field()
    special_conditions = Field()
    replenishment_ability = Field()
    replenishment_description = Field()
    min_irreducible_balance = Field()
    early_dissolution = Field()
    early_dissolution_description = Field()
    auto_prolongation = Field()
    auto_prolongation_description = Field()
    rates_table = Field()
    rates_comments = Field()
    online_opening = Field()
    partial_withdrawal = Field()
    partial_withdrawal_description = Field()
    updated_at = Field()
