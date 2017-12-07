# coding: utf-8

"""Development of NBA Fantasy News Scraper."""

import scrapy
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import re
import pandas as pd


base_url = 'https://www.cbssports.com/fantasy/basketball/players/news/all/'
pages = ['']
pages.extend(['{}/'.format(n) for n in range(2, 15)])
start_urls = ['{}{}'.format(base_url, p) for p in pages]


class FantasySpiderNBA(scrapy.Spider):
    """Instantiates Spider."""

    name = 'fantasy_spider_nba_local'
    start_urls = start_urls

    def parse(self, response):
        """Automatically parses url."""
        # get all relevant content
        content = response.css('ul.player-news-by-sport li')
        # player info is contained in column 3
        player_info = (content.css('div.col-3')
                       .css('div.players-annotated')
                       )
        # get list of players
        players = player_info.css('p a::text').extract()
        # get position | team info and split into pos and team info
        pos_team = player_info.css('p span::text').extract()
        positions = [p.split(' | ')[0].lstrip() for p in pos_team]
        teams = [
            p.split(' | ')[1]
            if len(p.split(' | ')) > 1
            else ''
            for p in pos_team
        ]
        # news info is contained in column 5
        news_info = (content.css('div.col-5')
                     .css('div.player-news-desc')
                     )
        # get the time of crawl and set to now
        now = datetime.now(timezone('EST'))
        # get time when news broke
        time_string = news_info.css('time.eyebrow::text').extract()
        # get simplified list of times
        time_string2 = [t.split(' ')[0] for t in time_string]
        # get time delta values
        delta_values = [
            int(re.findall(r'\d+', s)[0]) for s in time_string2
        ]
        # get time delta units
        delta_units = [s[-1] for s in time_string2]
        # using delta values and units, calculate time deltas
        update_times = []
        for dv, du in zip(delta_values, delta_units):
            if du == 'M':
                td = timedelta(minutes=dv)
            elif du == 'H':
                td = timedelta(hours=dv)
            elif du == 'D':
                td = timedelta(days=dv)
            else:
                td = timedelta(seconds=dv)
            update_times.append(now - td)
        # get headlines
        headlines = news_info.css('h4 a::text').extract()
        # get latest update text
        updates = news_info.css('div.latest-updates')
        update_text = []
        for update in updates:
            text = ' '.join(update.css('p::text').extract())
            update_text.append(text)
        # read in current fantasy news dataframe
        df_current = pd.read_csv('fantasy_news.csv')
        # set scraped information to dataframe
        df_new = pd.DataFrame({
            'team': teams,
            'player': players,
            'position': positions,
            'date': update_times,
            'text': [h + ' ' + u for h, u in zip(headlines, update_text)]
        })
        # concatenate new to current df and drop duplicates
        df_out = (
            pd.concat([df_current, df_new])
            .drop_duplicates(subset=['team', 'player', 'text'])
        )
        # write out complete df to fantasy news
        df_out.to_csv('fantasy_news.csv', index=False)
