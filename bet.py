import database as db
import scrape
#from bs4 import BeautifulSoup as bs4
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import time

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(executable_path="/home/matthew/Documents/git-repos/csgo-nn/chromedriver")
driver.get("https://loot2.bet/sport/esports/counter-strike")

def AddMatchesToBetSlip():
    time.sleep(2)
    PREDICTION_MIN_COEF = 60
    MATCH_MIN_ODDS = 1.8
    bettable_matches = driver.find_elements_by_tag_name("app-market")
    matches_db = db.get_not_bet_matches()
    for match in bettable_matches:
        team_b = match.find_element_by_class_name("teamRight")
        team_a = match.find_element_by_class_name("teamLeft")
        match_coefs_elements = match.find_elements_by_class_name("cof")
        match_coefs = (float(match_coefs_elements[0].text), float(match_coefs_elements[1].text))
        a_name = scrape.clean_name(team_a.text)
        b_name = scrape.clean_name(team_b.text)
        for match_db in matches_db:
            if match_db['team_a'] == a_name and match_db['team_b'] == b_name:
                coef = match_db['percentage_a_b'].split("/") 
                if int(coef[0]) > PREDICTION_MIN_COEF and match_coefs[0] >= MATCH_MIN_ODDS:
                  match_coefs_elements[0].click()
                elif int(coef[1]) > PREDICTION_MIN_COEF and match_coefs[1] >= MATCH_MIN_ODDS:
                  match_coefs_elements[1].click()
        

def Login():
    login_button = driver.find_element_by_xpath("//*[@id='main']/app-header/header/nav/div/div/a[3]")
    login_button.click()

    driver.implicitly_wait(5)
    form_username = driver.find_element_by_xpath("//*[@id='t-login']/app-authorization/form/div/div[1]/input")
    form_username.send_keys('bumbi@live.dk')

    form_password = driver.find_element_by_xpath("//*[@id='t-login']/app-authorization/form/div/div[2]/input")
    form_password.send_keys('NUTH.masm1douw')

    login_button = driver.find_element_by_xpath("//*[@id='t-login']/app-authorization/form/div/button")
    login_button.click()

def GetBettable():
    predicted_games = [ ["North", "mousesports", 0]]
    driver.get("https://loot2.bet/sport/esports/counter-strike")
    driver.implicitly_wait(5)
    game_table = driver.find_elements_by_class_name('mat-content')
    for game in game_table:
        for predicted_game in predicted_games:
            matchData = game.text.lower() 
            team1 = matchData.find(predicted_game[0])
            team2 = matchData.find(predicted_game[1])
            if team1 != -1 and team2 -1:
                betbuttons = game.find_elements_by_class_name("cof") 
                if predicted_game[2] == 0:
                    betbuttons[0].click()
                else:
                    betbuttons[1].click()
                break
                    

        
def main():
    #Login()
    #GetBettable()
    AddMatchesToBetSlip()
    pass


if __name__ == '__main__':
    main()
