import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, MapCompose, TakeFirst


class Rating(scrapy.Item):
    url = scrapy.Field()
    subject = scrapy.Field()

    # РЕЙТИНГ ЭКСПЕРТОВ
    experts = scrapy.Field()
    experts_min = scrapy.Field()
    experts_max = scrapy.Field()
    # РЕЙТИНГ ПОЛЬЗОВАТЕЛЕЙ
    users = scrapy.Field()
    users_min = scrapy.Field()
    users_max = scrapy.Field()
    # НАДЁЖНОСТЬ БУКМЕКЕРА
    reliability = scrapy.Field()
    reliability_min = scrapy.Field()
    reliability_max = scrapy.Field()
    # КОЭФФИЦИЕНТЫ
    ratio = scrapy.Field()
    ratio_min = scrapy.Field()
    ratio_max = scrapy.Field()
    # ВЫБОР СТАВОК
    variety = scrapy.Field()
    variety_min = scrapy.Field()
    variety_max = scrapy.Field()
    # БОНУСЫ И АКЦИИ
    bonuses = scrapy.Field()
    bonuses_min = scrapy.Field()
    bonuses_max = scrapy.Field()
    # ВЫВОД СРЕДСТВ
    withdrawal = scrapy.Field()
    withdrawal_min = scrapy.Field()
    withdrawal_max = scrapy.Field()
    # СЛУЖБА ПОДДЕРЖКИ
    support = scrapy.Field()
    support_min = scrapy.Field()
    support_max = scrapy.Field()


class RatingLoader(ItemLoader):
    default_item_class = Rating
    default_input_processor = MapCompose(float)
    default_output_processor = TakeFirst()

    url_in = Identity()
    subject_in = Identity()
