#!/usr/bin/env python
import cgi
import os
from django.utils import simplejson

from game_state import GameState

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext import db

def load_game_by_id(gid):
	""" TODO: use pickle to retrieve game state """
	# if game_state.id is None:
	# 	game_state.id = whatever
	return GameState('foo bar', 'baz mumble')

def store_game(game_state):
	""" TODO: pickle """
	if game_state.id is not None:
		# update the row
		pass
	else:
		# write, get the id, then update with the id
		pass

class Game(webapp.RequestHandler):
	""" This is the main view, it sets up all the state to render the game. """
	def get(self):
		game_id = self.request.get('gid')
		# TODO: validation, throw error if necessary
		game_state = load_game_by_id(game_id)

		template_values = {
			'game_state': game_state
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		""" TODO: create a new game for a pair of users from a form, save it, and redirect. """
		pass
		
class ShowMoves(webapp.RequestHandler):
	""" Responds to xhr requests when an insect is selected, to display where it can move. """
	def get(self):
		game_id = self.request.get('gid')
		game_state = load_game_by_id(game_id)

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
		game_state = load_game_by_id(game_id)

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
									('/', Game),
									('/show_moves', ShowMoves),
									('/move', Move),
									],
                                    debug=True)
def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
