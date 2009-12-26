from google.appengine.ext import db

class Game(db.Model):
    creator = db.UserProperty()
    opponent = db.UserProperty()
    game_state = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Table(db.Model):
	creator = db.UserProperty()
	empty_seat = db.BooleanProperty()
	game = db.ReferenceProperty(Game)
	date = db.DateTimeProperty(auto_now_add=True)

