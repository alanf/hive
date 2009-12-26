#!/usr/bin/env python
import copy

# Base class for all the insects. 
class Insect(object):
	def __init__(self):
		# None for not in play
		self.hex = None

class Spider(Insect):
	name = 'spider'

class Beetle(Insect):
	name = 'beetle'
	def __init__(self):
		super(Beetle, self).__init__()
		# the beetle can climb on other insects
		self.height = 0

class Grasshopper(Insect):
	name = 'grasshopper'

class Bee(Insect):
	name = 'bee'

class Ant(Insect):
	name = 'ant'

class Hex(object):
	""" Represents a single tile which may or may not have an insect. """
	def __init__(self, coord, is_playable=False, current_insect=None, is_visible=False):
		self.coord = coord
		self.id = '%s-%s' % self.coord
		self.current_insect = current_insect
		# TODO: better name, this var is for peripheral hexes
		self.is_visible = is_visible

class HiveBoard(object):
	""" A grid of hex tiles. Since insects can be placed forever in any direction,
		this will have to grow in a strange way, this is a TODO. """
	def __init__(self, size=7):
		# Row coordinates are backwards: y axis, x axis
		self.rows = []
		for i in range(size):
			row = []
			for j in range(size):
				row.append(Hex((j, i)))
			self.rows.append(row)

		# TODO math.ceil
		self.rows[3][3] = Hex((3, 3), is_playable=True, is_visible=True)
		self.start = self.rows[3][3]
	
	def get_by_id(self, target_id):
		coord = map(int, target_id.split('-'))
		return self.rows[coord[1]][coord[0]]

class GameState(object):
	""" Everything we need to store and successfully resume a game. """
	def __init__(self, white_player, black_player):
		self.white_player = white_player
		self.black_player = black_player
		self.current_turn = 'white'
		self.white_pieces = Spider(), Beetle(), Grasshopper(), Bee(), Ant(),
		self.black_pieces = copy.copy(self.white_pieces)
		self.board = HiveBoard()
		# Set the first time the game state is written to the store
		self.key = None
	
	def move(self, color, insect, target_id):
		""" Move a piece somewhere, throw an exception if it's not allowed. """
		if False:
			insect.hex = self.board.get_by_id(target)
			if self.current_turn == 'white':
				self.current_turn = 'black'
			else:
				self.current_turn = 'white'

		# TODO: need actual logic here, this is placeholder
		newly_visible = map(self.board.get_by_id, ['2-3', '3-4', '4-3', '3-2', '2-2', '4-2'])
		for a_hex in newly_visible:
			a_hex.is_visible = True
		no_longer_visible = []
		return newly_visible, no_longer_visible
		
	def show_moves(self, color, insect):
		""" Returns a list of hex ids that the insect can move to """
		# TODO: this is placeholder
		return [self.board.start]

	def check_move(self, color, insect, target_id):
		""" Returns True if the insect can move to the target. """
		pass

	def winner(self):
		""" Returns None if the game is not over or the color of the winning player. """
		pass
