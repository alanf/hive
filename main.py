#!/usr/bin/env python
import cgi
from collections import defaultdict
import os
import pickle
from django.utils import simplejson

from logic import GameState
from logic import Hex
import dbobjs

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class Create(webapp.RequestHandler):
	def get(self):
		""" Form to create a game. """
		path = os.path.join(os.path.dirname(__file__), 'templates', 'create.html')
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
			path = os.path.join(os.path.dirname(__file__), 'templates', 'table.html')
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
			game_state = GameState(game.creator, game.opponent)
			table.game = game_key = store_game(game_state)
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

def store_game(game_state):
	if game_state.key is None:
		game = dbobjs.Game()
		game.game_state = pickle.dumps(game_state)
		game.put()
		key = game.key()
		game_state.key = key
	else:
		# TODO: Careful here...validation could be useful
		game = db.get(game_state.key)

	# Store the game state with the key included
	game.game_state = pickle.dumps(game_state)
	game.put()
	return game.key()

def grid(board, min_size=7):
	""" Used to display the game board as a grid, so we can easily render it in the template. """
	grid = defaultdict(lambda : [])
	min_row = min_col = 0
	max_row = max_col = min_size
	# Put the hex in the right row. We'll sort by col at the end.
	for a_hex in board.hexes:
		coord = board._id_to_coord(a_hex.id)

		min_row = min(coord[0], min_row)
		max_row = max(coord[0], max_row)
		min_col = min(coord[1], min_col)
		max_col = max(coord[1], max_col)
		grid[coord[0]].append(a_hex)
	
	# Pad the grid with "missing" hexes
	for row in range(min_row, max_row):
		for col in range(min_col, max_col):
			temp_hex = Hex((row, col))
			if not board.get_by_id(temp_hex.id):
				grid[row].append(temp_hex)

	# Now make sure it's all in order
	for row in grid.values():
		# Sort inside each row by the x value of its coord, i.e. by column
		row.sort(lambda a, b: cmp(board._id_to_coord(a.id)[1], board._id_to_coord(b.id)[1]))
	
	return [grid[row] for row in range(min_row, max_row)]
		
class Game(webapp.RequestHandler):
	""" This is the main view, it sets up all the state to render the game. """
	def get(self):
		game_key = self.request.get('gid')
		# TODO: validation, throw error if necessary
		game_state = load_game_by_key(game_key)
		game_grid = grid(game_state.board)

		template_values = {
			'game_state': game_state,
			'game_grid': game_grid,
		}
		path = os.path.join(os.path.dirname(__file__), 'templates', 'game.html')
		self.response.out.write(template.render(path, template_values))
		
class Placement(webapp.RequestHandler):
	""" Called for when we want to add a new insect to the board. """
	def get(self):
		""" Displays where the insect can be placed. """
		game_key = self.request.get('gid')
		game_state = load_game_by_key(game_key)

		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		response = {
			'success': True,
			'hexes': game_state.show_placements(insect_color)
		}
		self.response.out.write(simplejson.dumps(response))

	def post(self):
		""" Respond to a request to place a new piece. """
		game_key = self.request.get('gid')
		game_state = load_game_by_key(game_key)

		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		target_hex = self.request.get('target_hex')

		result = game_state.placement(insect_color, insect_name, target_hex)
		response = {
			'success': True,
			'reveal_hex_ids': result,
		}
		store_game(game_state)
		self.response.out.write(simplejson.dumps(response))

class Move(webapp.RequestHandler):
	def get(self):
		""" Responds to xhr requests when an already placed insect is selected, to display where it can move. """
		game_key = self.request.get('gid')
		game_state = load_game_by_key(game_key)
		current_hex = self.request.get('current_hex')

		response = {
			'success': True,
			'hexes': [a_hex for a_hex in game_state.show_moves(current_hex)]
		}
		self.response.out.write(simplejson.dumps(response))

	def post(self):
		""" Submit a move and return what changed on the board, or an error. """
		# TODO: check for end of game conditions
		game_key = self.request.get('gid')
		game_state = load_game_by_key(game_key)

		current_hex = self.request.get('current_hex', None)
		target_hex = self.request.get('target_hex')

		# TODO: handle errors
		insect = game_state.move(current_hex, target_hex)
		response = {
			'success': True,
			'insect_name': insect.name,
			'insect_color': insect.color,
		}
		store_game(game_state)

		self.response.out.write(simplejson.dumps(response))
		

application = webapp.WSGIApplication([
									('^/$', Create),
									('^/create.*$', Create),
									('^/table.*$', Table),
									('^/game.*$', Game),
									('^/show_moves.*$', Move),
									('^/move.*$', Move),
									('^/show_available_placements.*$', Placement),
									('^/placement.*$', Placement),
									],
                                    debug=True)
def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
