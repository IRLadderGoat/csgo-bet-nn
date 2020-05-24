import MySQLdb as sql
import numpy as np
import datetime
import pandas as pd
import time
import re
from warnings import filterwarnings
filterwarnings('ignore', category = sql.Warning)

con = sql.connect (host = "localhost", user = "python", passwd = "matt0635", db = "hokkaido")
con.autocommit(True)
c = con.cursor(sql.cursors.DictCursor)
c_np = con.cursor()


def get_training_csv():
	csv_names = ['wins','elo','score','momentum','vs','rating','ts','outcome']
	df = pd.read_csv('data/training.csv', names=csv_names)
	array = df.values
	X = array[:,0:-1]
	y = array[:,-1]
	return X,y


def get_game_stats(table, game_id):
	c.execute ("SELECT * FROM %s WHERE id = %d ORDER BY id ASC LIMIT 1" % (table, game_id))	
	return c.fetchall()

def get_game_by_link(table, game_link):
	game_link = re.sub(r"\D", "", game_link)
	match_number = "%"+ game_link[:7] +"%"
	qry = "SELECT * FROM %s WHERE stats_url LIKE '%s'" % (table, match_number)
	c.execute(qry)
	return c.fetchone()

def get_most_recent_game(team):
	query_sql = "SELECT * FROM raw WHERE team_a = '%s' OR team_b = '%s'  ORDER BY date DESC LIMIT 1" % (team,team)
	rows_count = c.execute(query_sql)
	if rows_count > 0:
		return c.fetchone()
	else:
		return 0


def get_recent_total(team):
	query_sql = "SELECT * FROM processed WHERE team_a = '%s' OR team_b = '%s'  ORDER BY date DESC LIMIT 1" % (team,team)
	rows_count = c.execute(query_sql)
	if rows_count > 0:
		return c.fetchone()
	else:
		return 0


def get_team_by_slug(slug):
	query_sql = "SELECT * FROM teams WHERE slug = '%s' LIMIT 1" % (slug)
	rows_count = c.execute(query_sql)
	if rows_count > 0:
		return c.fetchone()
	else:
		return 0	


def get_random_game(table,i):
	query_sql = "SELECT * FROM %s ORDER BY id asc LIMIT 1 OFFSET %d" % (table,i)
	c.execute (query_sql)	
	return c.fetchone()


def get_team_prev_game(table, game_id, season, team):
	query_sql = "SELECT * FROM %s WHERE game_id > %d AND season = %d AND team = '%s' ORDER BY game_id ASC LIMIT 1" % (table, game_id, season, str(team))
	rows_count = c.execute(query_sql)
	if rows_count > 0:	
		return c.fetchone()
	else:
		return 0


def check_team_slug(code):
	query_sql = "SELECT * FROM teams WHERE team = '%s' LIMIT 1" % (str(code))
	rows_count = c.execute(query_sql)
	if rows_count > 0:
		return 1
	else:
		return 0


def check_game(game):
	query_sql = "SELECT * FROM raw WHERE team_a = '%s' AND team_b = '%s' AND date='%s' AND map='%s' AND a_score=%d AND b_score=%d LIMIT 1" % (game['team_a'],game['team_b'],game['date'],game['map'],int(game['a_score']),int(game['b_score']))
	rows_count = c.execute(query_sql)
	if rows_count > 0:
		return c.fetchone()
	else:
		return 0


def duplicate_delete(id,team_a,team_b,date,level,a_score,b_score):
	query_sql = "DELETE FROM raw WHERE team_a = '%s' AND team_b = '%s' AND date='%s' AND map='%s' AND a_score=%d AND b_score=%d AND id != %d" % (str(team_a),str(team_b),str(date),str(level),int(a_score),int(b_score),int(id))
	rows_count = c.execute(query_sql)
	return rows_count


def duplicate_delete(code,slug):
	query_sql = "DELETE FROM teams WHERE slug = '%s' AND code < %d" % (str(slug),int(code))
	rows_count = c.execute(query_sql)
	return rows_count


def get_uniq_teams():
	query_sql = "SELECT * FROM teams GROUP BY slug ORDER BY code DESC"
	c.execute(query_sql)	
	return c.fetchall()


def get_new_games():
	c.execute ("SELECT * FROM match_ids WHERE scraped = 0 ORDER BY id ASC")	
	return c.fetchall()


def get_all(table='raw',order_col='date',direction='ASC'):
	query_sql = "SELECT * FROM %s ORDER BY %s %s" % (table,order_col,direction)
	c.execute(query_sql)	
	return c.fetchall()


def get_active_teams():
	query_sql = "SELECT * FROM teams WHERE active = 1 AND code != 1111 ORDER BY RAND()"
	c.execute(query_sql)	
	return c.fetchall()


def get_missing_matches():
	query_sql = "SELECT * FROM raw WHERE stats = 0 ORDER BY id DESC"
	c.execute(query_sql)	
	return c.fetchall()

def get_predicted_matches_not_updated():
	qry = "SELECT * FROM graph WHERE winner = 0 ORDER BY id DESC"
	c.execute(qry)
	return c.fetchall()

def get_not_bet_matches():
	qry = "SELECT * FROM graph WHERE winner = 0 AND bet = 0 ORDER BY id DESC"
	c.execute(qry)
	return c.fetchall()

def insert_game(table, game):
	keys = game.keys()
	columns = ", ".join(keys)
	values_template = ", ".join(["%s"] * len(keys))

	sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns, values_template)
	values = tuple(game[key] for key in keys)
	c_np.execute(sql, values)

def insert_predicted_game(game, p1, p2):
	percentage_a_b = "%s/%s" % (p1,p2)
	predicted_winner = lambda t1, t2: 1 if (t1 > t2) else 2
	values = '\'%s\',\'%s\',\'%s\',\'%s\',\'0\',\'%s\'' % (game[0], game[1], percentage_a_b, predicted_winner(p1,p2), game[2])
	qry = 'INSERT INTO graph (team_a, team_b, percentage_a_b, predicted_outcome, winner, stats_url) VALUES (%s)' % (values)
	c.execute(qry)


def update_predicted_game(stat_url, outcome):
	qry = "UPDATE graph SET winner = '%s' WHERE stats_url = '%s'" % (outcome, stat_url)
	c.execute(qry)

def update_raw(p,game_id):
	qry = 'UPDATE raw SET a_kills = "%d", b_kills = "%d", a_deaths = "%d", b_deaths = "%d", a_adr = "%f", b_adr = "%f", a_kast = "%f", b_kast = "%f", a_rating = "%f", b_rating = "%f",stats = "%d"  WHERE id = %d' % (p['a_kills'],p['b_kills'],p['a_deaths'],p['b_deaths'],p['a_adr'],p['b_adr'],p['a_kast'],p['b_kast'],p['a_rating'],p['b_rating'],p['stats'],game_id)
	c.execute(qry)


def update_game(table, date,game_id):
	qry = 'UPDATE %s SET date = "%s" WHERE id = %d' % (table,date, game_id)
	c.execute(qry)


def update_order(order_id,game_id):
	qry = 'UPDATE raw SET game_order = "%d" WHERE id = %d' % (order_id, game_id)
	c.execute(qry)


def update_team_status(slug,active):
	qry = 'UPDATE teams SET active = %d WHERE slug = "%s"' % (active,slug)
	c.execute(qry)


def get_teams():
	c.execute ("SELECT * FROM teams WHERE active = 1 ORDER BY last_udpate ASC")	
	return c.fetchall()


def clear_table(table):
	query = "DELETE FROM %s WHERE 1" % (table)
	c.execute (query)

