## Требования
- [`Traefik`](https://github.com/weirdname404/traefik-daemon "Traefik")

## Quick Start
```shell
cp .env.example .env  # копируем дефолтные переменные среды
scripts/compose up -d --build  # хелпер для запуска сервиса с корректными пермишенами
export SCRAPY_PROJECT=sentiment_ru  # задаем sentiment_ru в качестве проекта
scripts/scrapyd list  # смотрим какие спайдеры доступны
scripts/scrapyd crawl itunes  # запускаем спайдер itunes
```
Посмотреть логи и собранные айтемы можно в:
- директории `./app/.scrapyd/`;
- админке https://scrapy.localhost/ (имя и пароль - те, что использовались при настройке Traefik).

## API
Поддерживаются [listspiders.json](https://scrapyd.readthedocs.io/en/stable/api.html#listspiders-json "listspiders.json") и [schedule.json](https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json "schedule.json"), через последний можно задавать/переопределять настройки проекта (`-d setting=настройка=значение`) и атрибуты скрапера (`-d атрибут=значение`). В основном это актуально для настроек вебхука:
- `WEBHOOK_ENABLED=True` вкл/выкл;
- `WEBHOOK_ENDPOINT=None` куда POST-запросом будет отправлен JSON с постами;
- `WEBHOOK_CHUNK_SIZE=1000` размер чанков с постами.

```shell
curl https://scrapy.localhost/schedule.json \
    -k \  # в dev среде могут быть проблемы с проверкой серта
    -u user:pass \  # имя и пароль - те, что использовались при настройке Traefik
    -d project=sentiment_ratings \
    -d spider=kushvsporte \
    -d setting=WEBHOOK_ENDPOINT=https://webhook.site/1a44e5a5-bd3b-45a2-9ee3-be4bacf39072 \
    -d setting=WEBHOOK_CHUNK_SIZE=10
```

###### Преобразовать curl-запрос во многие другие можно здесь: https://curl.trillworks.com/
