## Требования
[Traefik](https://github.com/weirdname404/traefik-daemon "Traefik")

## Quick Start
```shell
cp {,.}env
docker-compose up -d
curl http://localhost:6800/schedule.json -d project=sentiment_ru -d spider=itunes
```
Админка http://localhost:6800/

## Технологии
[Scrapy](https://docs.scrapy.org/en/latest/ "Scrapy")
[furl](https://github.com/gruns/furl "furl") для работы с парметрами запроса

## API
Поддерживаются [эндпоинты scrapyd](https://scrapyd.readthedocs.io/en/stable/api.html "эндпоинты scrapyd"), причем [schedule.json](https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json "schedule.json") расширен параметрами:
- `crawl_deep=0` каждый субъект парсится вглубь;
- `crawl_depth` глубина парсинга, зависит от источника;
- `webhook_url` куда POST-запросом будет отправлен JSON с постами;
- `webhook_chunk_size=1000` размер чанков с постами;
- `webhook_compat=0` режим совместимости со старыми скраперами.

```shell
curl http://localhost:6800/schedule.json \
    -d project=sentiment_ru \
    -d spider=kushvsporte \
    -d crawl_deep=1 \
    -d webhook_url=https://httpbin.org/post \
    -d webhook_chunk_size=9000
```
