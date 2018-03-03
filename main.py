import jinja2
import os
import webapp2
import logging
import json
from datetime import datetime, timedelta
from random import randint

from google.appengine.api import users

TEAM_MODE = False    #users are competing as individuals and having streaks

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(
		os.path.dirname(__file__)))

from models import *


def prettify_num(n):
	if n > 999: return ("%dk" % n/1000)
	return str(n)

class CommHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user: #redirect to login page
			pass
			return

		app_users = AppUser.query(AppUser.email==user.email()).fetch()

		if not app_users:
			app_user = AppUser(email=user.email()) 	
			app_user.total_donations = 0
			app_user.longest_streak = 0
			app_user.current_streak = 0
		else:
			app_user = app_users[0]


		team = AppUser.query(AppUser.teamid==app_user.teamid).fetch()
		
		variables = {
			'user_name':user.nickname(),
			'user_email':user.email(),
			'user_hashes':prettify_num(app_user.hashes),
			'team_hashes':prettify_num(sum(member.hashes for member in team)),
			'team':team,
		}
		template = jinja_environment.get_template('comm.html')
		self.response.write(template.render(variables))


class HasGivenHandler(webapp2.RequestHandler):
	def get(self):
		yesterday = datetime.now() - timedelta(hours=24)
		#email = self.request.get('email')
		user = users.get_current_user()
		email = user.email()
		app_users = AppUser.query(AppUser.email==email).fetch()
		if not app_users: return
		app_user = app_users[0]
		has_given_today = False
		if app_user.last_give_time > yesterday:
			has_given_today = True
		self.response.write(json.dumps({'has_given_today':has_given_today}))

class StatsHandler(webapp2.RequestHandler):
	def get(self):
		'''returns team size, total donations, total team donations, highscores'''
		user = users.get_current_user()
		app_user = AppUser.query(AppUser.email==user.email()).fetch()[0]
		team = AppUser.query(AppUser.teamid==app_user.teamid).fetch()
		self.response.write(json.dumps({'team_size':len(team), 'total_donations':app_user.total_donations, 'total_team_donations':sum(x.total_donations for x in team), 'current_streak':app_user.current_streak, 'longest_streak':app_user.longest_streak}))

		
class PlayHandler(webapp2.RequestHandler):
	def get(self):
		give = self.request.get('give') or '0'    #bool
		give = bool(int(give))
		user = users.get_current_user()
		if not user: return
		app_users = AppUser.query(AppUser.email==user.email()).fetch()
		if not app_users: return
		app_user = app_users[0]
		team = AppUser.query(AppUser.teamid==app_user.teamid).fetch()

		if give:
			#update stats
			#affect donation (mining donation is done clientside)
			app_user.hashes += randint(1, 10000)
			app_user.last_give_time = datetime.now()
			app_user.current_streak += 1
			app_user.total_donations += app_user.default_donation
			app_user.put()
			#if everyone donated this round
			#or maybe flip a coin to see if we get to merge

			#get list of users with the same streak
			other_players = AppUser.query(AppUser.current_streak==app_user.current_streak, AppUser.teamid!=app_user.teamid).fetch()

			#merge current_player into their team
			if other_players:
				for team_player in team:
					team_player.teamid = other_players[0].teamid

		else:
			#reset team and streaks
			for team_player in team:
				team_player.longest_streak = max(team_player.current_streak, team_player.longest_streak)
				team_player.current_streak = 0
				team_player.teamid = user.user_id()    #we're using userid to create a unique team id
				team_player.put()

class SettingsHandler(webapp2.RequestHandler):
	def get(self):
		#creates account if there isn't one already
		#set default donation amount, etc
		default_donation = self.request.get('default_donation') or 5
		default_donation = float(default_donation)
		user = users.get_current_user()
		if not user: return
		app_users = AppUser.query(AppUser.email==user.email()).fetch()
		if not app_users: 
			app_user = AppUser(email=user.email()) 	
			app_user.total_donations = 0
			app_user.longest_streak = 0
			app_user.current_streak = 0
			app_user.hashes = 0
		else:
			app_user = app_users[0]
		app_user.default_donation = default_donation
		app_user.teamid = user.user_id()
		app_user.put()

class HomepageHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		auth_link = '<a class="nav-link" href="%s">%s</a>' % ((users.create_logout_url('/'), 'Sign out') if user else (users.create_login_url(), 'Sign in'))
		template = jinja_environment.get_template('home.html')
		self.response.write(template.render({'auth_link':auth_link}))

class AboutusHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		auth_link = '<a class="nav-link" href="%s">%s</a>' % ((users.create_logout_url('/'), 'Sign out') if user else (users.create_login_url(), 'Sign in'))
		template = jinja_environment.get_template('about.html')
		self.response.write(template.render({'auth_link':auth_link}))

app = webapp2.WSGIApplication([
	('/hasgiven/', HasGivenHandler),
	('/stats/', StatsHandler),
	('/play/', PlayHandler),
	('/settings/', SettingsHandler),
    ('/', HomepageHandler),
    ('/comm/', CommHandler),
    ('/aboutus/', AboutusHandler), #('/register/', CreateUserHandler),
], debug=True)

