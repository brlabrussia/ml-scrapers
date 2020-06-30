# This file must be used with "source helpers.sh" *from bash* you cannot run it directly

# Add "[[ -f helpers.sh ]] && . helpers.sh" to .bashrc to source automatically

# Workflow:
#
# Set project variable for latter commands
# > export SCRAPY_PROJECT=sentiment_ratings
#
# Start scrapy shell session for url from within docker container
# > ss https://kushvsporte.ru/bookmaker/fonbet
#
# Start scrapyd job for kushvsporte spider from within docker container
# Logs and scraped items will be available at ./app/.scrapyd/ as well as at traefik host
# > sc kushvsporte

alias sc='scrapy_crawl'
function scrapy_crawl {
    # If SCRAPY_PROJECT is set, use it as project instead of first argument
    if [[ -v SCRAPY_PROJECT ]]; then
        project=$SCRAPY_PROJECT
        spider=$1
        argv=${@:2}
    else
        project=$1
        spider=$2
        argv=${@:3}
    fi
    # Prepare the command which will be passed to the container
    service_command="curl localhost:6800/schedule.json -d project=$project -d spider=$spider $argv"
    # Echo command before execution, parens are used to launch in subshell and avoid "set +x"
    ( set -x ; docker-compose exec app sh -c "$service_command" )
}

alias ss='scrapy_shell'
function scrapy_shell {
    if [[ -v SCRAPY_PROJECT ]]; then
        project=$SCRAPY_PROJECT
        spider=$1
        argv=${@:2}
    else
        project=$1
        spider=$2
        argv=${@:3}
    fi
    service_command="SCRAPY_PROJECT=$project scrapy shell $spider $argv"
    ( set -x ; docker-compose exec app sh -c "$service_command" )
}
