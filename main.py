#!/usr/bin/env python
import cgi
import os
import pickle
from django.utils import simplejson

from logic import GameState
import dbobjs

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class Create(webapp.RequestHandler):
	def get(self):
		""" Form to create a game. """
		path = os.path.join(os.path.dirname(__file__), 'create.html')
		self.response.out.write(template.render(path, {}))
	
	def post(self):
		""" Creating a game. """
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		table = dbobjs.Table()
		table.creator=user
		table.empty_seat=True
		table.game=None
		table.put()

		self.redirect('/table.html?tid=' + str(table.key()))
		
class Table(webapp.RequestHandler):
	def get(self):
		""" Waiting for another player to join, or joining the game. """
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		table_key = self.request.get('tid')
		table = db.get(table_key)

		if table.empty_seat:
			if user == table.creator:
				is_creator = True
			else:
				is_creator = False
			path = os.path.join(os.path.dirname(__file__), 'table.html')
			self.response.out.write(template.render(path, {
				'table_key': table_key,
				'is_creator': is_creator,
			}))
		# otherwise redirect to the game (xhr)
		else:
			self.redirect('/game.html?gid=' + str(table.game))
	
	def post(self):
		""" Joining the game """
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		table_key = self.request.get('tid')
		table = db.get(table_key)

		# TODO: this needs to be a transaction
		if table.empty_seat:
			table.empty_seat = False
			# Create a new game
			# TODO: will need new logic for games in progress
			game = dbobjs.Game()
			game.creator = table.creator
			game.opponent = user
			# TODO: use their nicknames or ids or something
			game_state = GameState(game.creator, game.opponent)
			table.game = game_key = store_game(game, game_state)
			table.put()
		else:
			game_key = table.game
		self.redirect('/game.html?gid=' + str(game_key))


def load_game_by_key(key):
	try:
		game = db.get(key)
		return pickle.loads(game.game_state)
	except:
		return None

def store_game(game, game_state):
	game = dbobjs.Game()
	game.game_state = pickle.dumps(game_state)
	if game_state.key is None:
		# TODO: write twice, so we can store the key. There's a better way...
		game.put()
		key = game.key()
		game_state.key = key
	game.game_state = pickle.dumps(game_state)
	game.put()
	return game.key()

class Game(webapp.RequestHandler):
	""" This is the main view, it sets up all the state to render the game. """
	def get(self):
		game_id = self.request.get('gid')
		# TODO: validation, throw error if necessary
		game_state = load_game_by_key(game_id)

		template_values = {
			'game_state': game_state
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		
class ShowMoves(webapp.RequestHandler):
	""" Responds to xhr requests when an insect is selected, to display where it can move. """
	def get(self):
		game_id = self.request.get('gid')
		game_state = load_game_by_key(game_id)

		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		response = {
			'success': True,
			'hexes': [a_hex.id for a_hex in game_state.show_moves(insect_color, insect_name)]
		}
		self.response.out.write(simplejson.dumps(response))
		
class Move(webapp.RequestHandler):
	""" Respond to xhr when an insect is moved to a specific hex tile. """
	def post(self):
		""" Submit a move and return what changed on the board, or an error. """
		# TODO: check for end of game conditions
		game_id = self.request.get('gid')
		game_state = load_game_by_key(game_id)

		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		target_hex = self.request.get('target_hex')

		try:
			result = game_state.move(insect_color, insect_name, target_hex)
			response = {
				'success': True,
				'reveal_hex_ids': [a_hex.id for a_hex in result[0]],
				'hide_hex_ids': [a_hex.id for a_hex in result[1]],
			}
		except:
			response = {
				'success': False,
				'msg': 'Something went wrong, :-/'
			}

		self.response.out.write(simplejson.dumps(response))
		

application = webapp.WSGIApplication([
									('^/create.*$', Create),
									('^/table.*$', Table),
									('^/game.*$', Game),
									('^/show_moves.*$', ShowMoves),
									('^/move.*$', Move),
									],
                                    debug=True)
def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
