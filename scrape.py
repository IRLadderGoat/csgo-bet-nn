from __future__ import division
import re
import urllib.request
from bs4 import BeautifulSoup as bs
import database as db
import time

def load_page(page_url):
    try:
        req = urllib.request.Request(
            page_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'})
        html = urllib.request.urlopen(req).read()
        soup = bs(html, 'html.parser')
        return soup
    except Exception as e:
        print("/n/n#######   Error Loading URL   ####### /n/n")
        print(page_url)
        print(e)
        return 0


def find_new_games():
    new_games = scrape_matches()
    new_games.reverse()
    print("\nNew Games:",len(new_games))
    for game in new_games:
        db.insert_game('raw', game)


def match_details():
    print("Getting missing matches")
    games = db.get_missing_matches()
    gameNum = 0
    gamesTotal = len(games)
    for g in games:
        time.sleep(0.5)
        team = 'a'
        players = {'a_kills':0,'a_deaths':0,'a_kast':0,'a_adr':0,'a_rating':0,'b_kills':0,'b_deaths':0,'b_kast':0,'b_adr':0,'b_rating':0,'stats':1}
        print("Updated game %d out of %d total" % (gameNum, gamesTotal), end='\r')
        try:
            soup = load_page('https://www.hltv.org'+g['stats_url'])
            for tables in soup.find_all('table',{'class':'stats-table'}):
                tbody = tables.find('tbody')
                for tr in tbody.find_all('tr'):
                    tds = tr.find_all('td')
                    kast = tds[4].text.replace('%','')
                    kast = kast.replace('-','0')
                    adr = tds[6].text.replace('-','0')

                    players[team+'_kills'] += int(clean_name(re.sub('[^a-zA-Z0-9 -]', '', tds[1].text[:-3])))
                    players[team+'_deaths'] += int(tds[3].text)
                    players[team+'_adr'] += round(float(adr),2)
                    players[team+'_kast'] += round(float(kast),2)
                    players[team+'_rating'] += round(float(tds[8].text),2)
                team = 'b'
            db.update_raw(players,g['id'])
            gameNum += 1
        except Exception as e:
            print(e)
            continue


def scrape_matches():
    print("Scraping new matches")
    new_games = []
    offset = 0
    date = 0
    while(1):
        page = offset * 50
        time.sleep(0.5)
        soup = load_page('https://www.hltv.org/stats/matches?offset='+str(page))

        match_table = soup.find("table", { "class" : 'matches-table'})
        tbody = match_table.find('tbody')
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')

            a_score = clean_name(tds[1].find('span',{'class':'score'}).text)
            b_score = clean_name(tds[2].find('span',{'class':'score'}).text)

            try:
                if int(a_score) > int(b_score):
                    outcome = 1
                else:
                    outcome = 0
            except Exception:
                #print("Message: %s \na_score: %s \nb_score %s" % e.message, a_score, b_score)
                print("Failed retrieving scores")


            game = {
                'team_a': clean_name(re.sub('[^a-zA-Z0-9 -]', '', tds[1].text[0:-3])),
                'team_b': clean_name(re.sub('[^a-zA-Z0-9 -]', '', tds[2].text[0:-3])),
                'a_score':a_score,
                'b_score':b_score,
                'map':clean_name(tds[3].find('div',{'class':'dynamic-map-name-short'}).text),
                'outcome': outcome,
                'date': re.sub("[^0-9]", "", tds[0].text),
                'stats_url': tds[0].find('a', href=True)['href'],
            }
            if game['team_a'] != '' and game['team_b'] != '':
                new_team_check(game['team_a'])
                new_team_check(game['team_b'])

                if db.check_game(game) == 0:
                    new_games.append(game)
                    if game["date"] != date:
                        date = game["date"]
                        print("Checking date: %s" % (date), end='\r')
                else:
                    return new_games
        offset+=1

def upcoming_matches():
    print("Getting upcoming matches")
    matches = []
    soup = load_page('https://www.hltv.org/')
    column = soup.find("div", { "class" : 'top-border-hide' })
    upcoming = column.find_all("div", { "class" : 'teamrows' })
    links = column.find_all('a')
    linkIter = iter(links)
    print("\nScraping Upcoming Matches:")
    for teams in upcoming:
        t = teams.find_all("div",{'class':'teamrow'})
        team_a = clean_name(t[0].text)
        team_b = clean_name(t[1].text)
        match_link = next(linkIter)['href']
        matches.append([team_a,team_b, match_link])
    return matches


def new_team_check(team_name):
    if db.check_team_slug(team_name) < 1:
        team = {'team': team_name}
        db.insert_game('teams', team)

def insert_predicted_match(game, p1, p2):
    result = db.get_game_by_link("graph", game[2])
    if result != None:
        return False
    else:
        db.insert_predicted_game(game, p1, p2)
        return True

def update_predicted_matches():
    matches = db.get_predicted_matches_not_updated()
    for match in matches:
        time.sleep(0.5)
        soup = load_page('https://www.hltv.org'+match['stats_url'])
        score = soup.find("div", {"class": 'standard-box teamsBox'})
        try:
            winner = score.find("div", {"class": 'won'}).parent['class'][0]
            if "1" in winner:
                db.update_predicted_game(match['stats_url'], '1')
            else:
                db.update_predicted_game(match['stats_url'], '2')
            #print("Updated match\n\t", match['stats_url'])
        except:
            pass

def clean_name(team_name):
    clean_name = re.sub('[^A-Za-z0-9]+', '', team_name)
    slug = re.sub(r'\W+', '', str(clean_name).lower().strip())
    return slug


def main():
    print("Finding New Games...\n")
    find_new_games()
    print("Fetching Match Details...\n")
    match_details()


if __name__ == "__main__":
    main()

