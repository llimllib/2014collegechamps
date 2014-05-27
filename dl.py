import cPickle
import csv
import os
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://play.usaultimate.org"

def get_match_urls():
    # Get all match reports
    r = requests.get(BASE_URL + "/events/USA-Ultimate-D-I-College-Championships/schedule/Mens/College-x-College/")
    soup = BeautifulSoup(r.text)
    reports = soup.findAll("a", attrs={"href": re.compile("EventGameId")})
    report_urls = [report.attrs["href"] for report in reports]
    return report_urls

class Stats(object):
    def __init__(self, name, goals, assists, ds, turns, team):
        self.name = name
        self.goals = goals
        self.assists = assists
        self.ds = ds
        self.turns = turns
        self.team = team

    def __add__(self, other):
        return Stats(self.name, self.goals+other.goals,
                self.assists+other.assists, self.ds+other.ds,
                self.turns+other.turns, self.team)

def parsetable(div, team):
    table = {}
    stats = div.find("table", attrs={"class": "global_table"})
    for row in stats.findAll("tr")[1:]:
        name, goals, assists, ds, turns = [r.text.strip() for r in row.findAll("td")]
        assert name, "Couldn't find name in row %s" % row
        table[name] = Stats(name, goals, assists, ds, turns, team)
    return table

def get_gamestats(report_urls):
    gamestats = {}

    # For each match report, pull out the stats
    for report_url in report_urls:
        r = requests.get(BASE_URL + report_url)
        gameid = re.search("GameId=(.*)", report_url).groups()[0]
        soup = BeautifulSoup(r.text)

        homediv = soup.find("div", attrs={"id": "home_team"})
        hometeam = homediv.find('span').text
        homestats = parsetable(homediv, hometeam)

        awaydiv = soup.find("div", attrs={"id": "away_team"})
        awayteam = awaydiv.find('span').text
        awaystats = parsetable(awaydiv, awayteam)

        gamestats[gameid] = {
            "home": {
                "name": hometeam,
                "stats": homestats
            },
            "away": {
                "name": awayteam,
                "stats": awaystats
            },
        }

    return gamestats

def get_playerstats(gamestats):
    playerstats = {}

    for gameid, game in gamestats.iteritems():
        hometeam = game["home"]["name"]
        homestats = game["home"]["stats"]
        awayteam = game["away"]["name"]
        awaystats = game["away"]["stats"]

        allstats = homestats.copy()
        allstats.update(awaystats)

        for player, stats in allstats.iteritems():
            if player not in playerstats:
                playerstats[player] = stats
            else:
                playerstats[player] = playerstats[player] + stats

    return playerstats

def write_csv(fout):


def load_or_run(filename, function, *args):
    if not os.path.isfile(filename):
        result = function(*args)
        cPickle.dump(result, file(filename, 'w'))
    else:
        result = cPickle.load(file(filename))

    return result

if __name__=="__main__":
    print "getting match URLs"
    report_urls = load_or_run("match_urls.pkl", get_match_urls)
    print "getting game stats"
    gamestats = load_or_run("gamestats.pkl", get_gamestats, report_urls)
    print "generating player summaries"
    playerstats = load_or_run("playerstats.pkl", get_playerstats, gamestats)
