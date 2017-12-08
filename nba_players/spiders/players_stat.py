import scrapy




import requests
import csv
import sys

# get me all active players

url_allPlayers = ("http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason"
		"=0&LeagueID=00&Season=2015-16")

#request url and parse the JSON
response = requests.get(url_allPlayers)
response.raise_for_status()
players = response.json()['resultSets'][0]['rowSet']

# use roster status flag to check if player is still actively playing
active_players = [players[i] for i in range(0,len(players)) if players[i][2]==1 ]

ids = [active_players[i][0] for i in range(0,len(active_players))]

print("Number of Active Players: " + str(len(ids)))

### https://gist.github.com/timmyshen/32d682c7b8aef014c256


class PlayerStats(scrapy.Spider):
    name = "nba_palayer_stats"
    start_urls = [
        'http://stats.nba.com/players/list/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)