import scrapy
from datetime import datetime
from datetime import timedelta
#from pytz import timezone
import re
import pandas as pd



import requests
import csv
import sys

# get me all active players

# url_allPlayers = "http://stats.nba.com/stats/commonallplayers?IsOnlyCurrentSeason=0&LeagueID=00&Season=2017-18"

# request url and parse the JSON
# response = requests.get(url_allPlayers)
# response.raise_for_status()
# players = response.json()['resultSets'][0]['rowSet']

# use roster status flag to check if player is still actively playing
# active_players = [players[i] for i in range(0,len(players)) if players[i][2]==1 ]

# ids = [active_players[i][0] for i in range(0,len(active_players))]

# print("Number of Active Players: " + str(len(ids)))

# https://gist.github.com/timmyshen/32d682c7b8aef014c256


class PlayerStats(scrapy.Spider):
    name = "nba_player_stats"
    url_begin = ''

    # start_urls = [ url_begin+id for id in ids ]
    start_urls = ['http://stats.nba.com/player/203518/', 'http://stats.nba.com/player/203084/']

    def parse(self, response):
        for url in url_players:#in response.css('div.quote'):
            yield scrapy.Request(url, callback=self.parse_player_stats)

        # next_page = response.css('li.next a::attr(href)').extract_first()
        # if next_page is not None:
            # next_page = response.urljoin(next_page)
            # yield scrapy.Request(next_page, callback=self.parse)

    def parse_player_stats(self, response):
        item = NbaPlayersItem()
        item['name'] = response.xpath().extract()