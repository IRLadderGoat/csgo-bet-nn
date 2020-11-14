import database as db
import scrape
#from bs4 import BeautifulSoup as bs4
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import time

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
driver.get("https://loot2.bet/sport/esports/counter-strike")

PREDICTION_MIN_COEF = 60
MATCH_MIN_ODDS = 1.8
SINGLE_BET = True

def AddMatchesToBetSlip():
    time.sleep(5)

    bettable_matches = driver.find_elements_by_tag_name("app-market")
    matches_db = db.get_not_bet_matches()
    for match in bettable_matches:
        team_b = match.find_element_by_class_name("teamRight")
        team_a = match.find_element_by_class_name("teamLeft")
        site_coefs_elements = match.find_elements_by_class_name("cof")
        site_coefs = (float(site_coefs_elements[0].text), float(site_coefs_elements[1].text))
        a_name = (team_a.text).split('\n')[0].lower()
        b_name = (team_b.text).split('\n')[0].lower()
        for match_db in matches_db:
            if match_db['team_a'] == a_name and match_db['team_b'] == b_name:
                coef = match_db['percentage_a_b'].split("/") 
                if float(coef[0]) > PREDICTION_MIN_COEF and site_coefs[0] >= MATCH_MIN_ODDS:
                  site_coefs_elements[0].click()
                elif float(coef[1]) > PREDICTION_MIN_COEF and site_coefs[1] >= MATCH_MIN_ODDS:
                  site_coefs_elements[1].click()
        

def Login():
    driver.implicitly_wait(2)

    login_button = driver.find_element_by_xpath("//*[@id='main']/app-header/header/nav/div[2]/div/a[1]")
    login_button.click()

    driver.implicitly_wait(2)
    form_username = driver.find_element_by_xpath("//*[@id='main']/app-header/app-modal[2]/div/div[1]/div/section/div/app-authorization/form/div/div[1]/input")
    form_username.send_keys('bumbi@live.dk')

    form_password = driver.find_element_by_xpath("//*[@id='main']/app-header/app-modal[2]/div/div[1]/div/section/div/app-authorization/form/div/div[2]/input")
    form_password.send_keys('NUTH.masm1douw')

    driver.implicitly_wait(70)

    login_button = driver.find_element_by_xpath("//*[@id='main']/app-header/app-modal[2]/div/div[1]/div/section/div/app-authorization/form/div/button")
    login_button.click()

def place_bets():
    #betable_amount = get_balance()/15
    betable_amount = 1.0
    #if betable_amount < 10:
        #return
    if SINGLE_BET:
        tab_button = driver.find_element_by_class_name('nav-item.das')
        tab_button.click()
        allow_new_coef = driver.find_element_by_css_selector("label[class='custom-control-label']")
        allow_new_coef.click()


        matches = driver.find_elements_by_class_name('calc-bet')
        for match in matches:
            input_field = match.find_element_by_css_selector("input[type='text']")
            input_field.send_keys(str(betable_amount))
        



def get_balance():
    return float(driver.find_element_by_class_name('dropdown-menu_current-balance').text)

# def GetBettable():
#     predicted_games = [ ["North", "mousesports", 0]]
#     driver.get("https://loot2.bet/sport/esports/counter-strike")
#     driver.implicitly_wait(5)
#     game_table = driver.find_elements_by_class_name('mat-content')
#     for game in game_table:
#         for predicted_game in predicted_games:
#             matchData = game.text.lower() 
#             team1 = matchData.find(predicted_game[0])
#             team2 = matchData.find(predicted_game[1])
#             if team1 != -1 and team2 -1:
#                 betbuttons = game.find_elements_by_class_name("cof") 
#                 if predicted_game[2] == 0:
#                     betbuttons[0].click()
#                 else:
#                     betbuttons[1].click()
#                 break
                    

        
def main():
    #Login()
    #GetBettable()
    #AddMatchesToBetSlip()
    place_bets()
    pass


if __name__ == '__main__':
    main()
