#import database as db
#import scrape
#from bs4 import BeautifulSoup as bs4
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
driver.get("https://loot2.bet/sport/esports/counter-strike")

def AddMatchesToBetSlip():
    pass

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
    GetBettable()
    pass


if __name__ == '__main__':
    main()