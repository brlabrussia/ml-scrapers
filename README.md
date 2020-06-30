## Требования
- [`Traefik`](https://github.com/weirdname404/traefik-daemon "Traefik")

## Quick Start
```shell
cp .env.example .env
docker-compose up -d
source helpers.sh
sc sentiment_ru itunes  # sc имя-проекта имя-скрапера
```
Посмотреть логи и собранные айтемы можно в:
- директории `./app/.scrapyd/`;
- админке https://scrapy.localhost/ (имя и пароль - те, что использовались при настройке Traefik).

## API
Поддерживаются [listspiders.json](https://scrapyd.readthedocs.io/en/stable/api.html#listspiders-json "listspiders.json") и [schedule.json](https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json "schedule.json"), через последний можно задавать/переопределять настройки проекта (`-d setting=настройка=значение`) и атрибуты скрапера (`-d аттрибут=значение`). В основном это актуально для настроек вебхука:
- `WEBHOOK_ENABLED=True` вкл/выкл;
- `WEBHOOK_ENDPOINT=None` куда POST-запросом будет отправлен JSON с постами;
- `WEBHOOK_CHUNK_SIZE=1000` размер чанков с постами;
- `WEBHOOK_COMPAT=False` режим совместимости со старыми скраперами `sentiment_ru`.

```shell
curl https://scrapy.localhost/schedule.json \
    -u user:pass \  # имя и пароль - те, что использовались при настройке Traefik
    -d project=sentiment_ratings \
    -d spider=kushvsporte \
    -d setting=WEBHOOK_ENDPOINT=https://webhook.site/1a44e5a5-bd3b-45a2-9ee3-be4bacf39072 \
    -d setting=WEBHOOK_CHUNK_SIZE=10
```

Преобразовать curl-запрос во многие другие можно здесь: https://curl.trillworks.com/

## API (Legacy и `sentiment_ru`)
Вышеописанный пайплайн также поддерживает задания параметров через атрибуты скрапера:
- `webhook_url` куда POST-запросом будет отправлен JSON с постами;
- `webhook_chunk_size=1000` размер чанков с постами;
- `webhook_compat=0` режим совместимости со старыми скраперами.
Также скраперы `sentiment_ru` поддерживают:
- `crawl_deep=0` каждый субъект парсится вглубь;
- `crawl_depth` глубина парсинга, зависит от источника.

```shell
curl http://localhost:6800/schedule.json \
    -d project=sentiment_ru \
    -d spider=kushvsporte \
    -d crawl_deep=1 \
    -d webhook_url=https://httpbin.org/post \
    -d webhook_chunk_size=9000
```
