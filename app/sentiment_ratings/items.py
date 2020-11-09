from statistics import mean

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose, Identity, Join, MapCompose


class TakeFirstOrNull:
    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return value
        else:
            return None


class Rating(scrapy.Item):
    # default.pipelines.ScrapyMetaFieldPipeline
    scrapy_project = scrapy.Field()
    scrapy_spider = scrapy.Field()

    # default.pipelines.SentimentSourceFieldPipeline
    source = scrapy.Field()

    # Meta
    url = scrapy.Field()
    subject = scrapy.Field()

    # Дефолт для всех полей
    min = scrapy.Field()
    max = scrapy.Field()

    # Рейтинг экспертов
    experts = scrapy.Field()
    experts_min = scrapy.Field()
    experts_max = scrapy.Field()

    # Рейтинг пользователей
    users = scrapy.Field()
    users_min = scrapy.Field()
    users_max = scrapy.Field()

    # Надёжность
    reliability = scrapy.Field()
    reliability_min = scrapy.Field()
    reliability_max = scrapy.Field()

    # Коэффициенты
    ratio = scrapy.Field()
    ratio_min = scrapy.Field()
    ratio_max = scrapy.Field()

    # Выбор ставок: (Лайв + Прематч) / 2
    variety = scrapy.Field()
    variety_min = scrapy.Field()
    variety_max = scrapy.Field()

    # Бонусы
    bonuses = scrapy.Field()
    bonuses_min = scrapy.Field()
    bonuses_max = scrapy.Field()

    # Вывод средств
    withdrawal = scrapy.Field()
    withdrawal_min = scrapy.Field()
    withdrawal_max = scrapy.Field()

    # Служба поддержки
    support = scrapy.Field()
    support_min = scrapy.Field()
    support_max = scrapy.Field()


class RatingLoader(ItemLoader):
    default_item_class = Rating
    default_input_processor = MapCompose(float)
    default_output_processor = TakeFirstOrNull()

    url_in = Identity()
    subject_in = MapCompose(str.strip)
    variety_out = Compose(mean)


def championat_classes_to_rating(value):
    if '_good' in value:
        return 100
    elif '_middle' in value:
        return 80
    elif '_bad' in value:
        return 60


class ChampionatLoader(RatingLoader):
    default_input_processor = MapCompose(
        championat_classes_to_rating,
        float,
    )

    min_in = max_in = MapCompose(float)
    subject_out = Join('')


def legalbet_classes_to_rating(value):
    if 'good' in value:
        return 100
    elif 'medium' in value:
        return 80
    elif 'bad' in value:
        return 60


class LegalbetLoader(RatingLoader):
    default_input_processor = MapCompose(
        legalbet_classes_to_rating,
        float,
    )

    min_in = max_in = MapCompose(float)
    subject_out = Join('')
    reliability_in = MapCompose(float)
