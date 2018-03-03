from google.appengine.ext import ndb

class AppUser(ndb.Model):
	default_donation = ndb.FloatProperty()
	email = ndb.StringProperty()
	teamid = ndb.StringProperty()
	total_donations = ndb.FloatProperty()
	longest_streak = ndb.IntegerProperty()
	current_streak = ndb.IntegerProperty()
	last_give_time = ndb.DateTimeProperty()
	hashes = ndb.IntegerProperty()
	
