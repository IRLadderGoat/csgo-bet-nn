from flask import Flask, render_template
import MySQLdb as sql

con = sql.connect (host = "localhost", user = "python", passwd = "matt0635", db = "hokkaido")
con.autocommit(True)
c = con.cursor(sql.cursors.DictCursor)
c_np = con.cursor()

app = Flask(__name__)

@app.route('/')
def entry_page():
    c.execute ("SELECT * FROM graph WHERE winner = 0 ORDER BY id DESC LIMIT 20")	
    upcoming_games = c.fetchall()
    c.execute ("SELECT * FROM graph WHERE winner <> 0 ORDER BY id DESC LIMIT 20")	
    ended_games = c.fetchall()
    c.execute ("SELECT COUNT(*) FROM graph WHERE winner = predicted_outcome")	
    wins = c.fetchone()
    wins = wins['COUNT(*)']
    c.execute ("SELECT COUNT(*) FROM graph WHERE winner <> predicted_outcome")	
    losses = c.fetchone()
    losses = losses['COUNT(*)']
    total = wins+losses
    c.execute ("SELECT COUNT(*) FROM graph WHERE winner = predicted_outcome AND haveBet = 1")	
    bet_wins = c.fetchone()
    bet_wins = wins['COUNT(*)']
    c.execute ("SELECT COUNT(*) FROM graph WHERE winner <> predicted_outcome AND haveBet = 1")	
    bet_loss = c.fetchone()
    bet_loss = wins['COUNT(*)']
    bet_per = bet_wins/(bet_loss+bet_wins)

    win_per = round((wins/total)*100, 2)
    return render_template('index.html', upcoming_games=upcoming_games,
                                         ended_games=ended_games,
                                         wins=wins,
                                         losses=losses,
                                         win_per=win_per,
                                         total=total,
                                         bet_per=bet_per)

if __name__ == '__main__':
   app.run(debug = True)