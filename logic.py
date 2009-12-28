#!/usr/bin/env python

# Base class for all the insects. 
class Insect(object):
	def __init__(self, color):
		# None for not in play
		self.hex_id = None
		self.color = color

class Spider(Insect):
	name = 'spider'

class Beetle(Insect):
	name = 'beetle'
	def __init__(self, color):
		super(Beetle, self).__init__(color)
		# the beetle can climb on other insects
		self.height = 0

class Grasshopper(Insect):
	name = 'grasshopper'

class Bee(Insect):
	name = 'bee'

class Ant(Insect):
	name = 'ant'

class Hex(object):
	""" Represents a single tile which may contain multiple insects. """
	def __init__(self, coord, is_visible=False):
		self.coord = coord
		self.id = '%s-%s' % self.coord
		self.insects = []
		# TODO: better name, this var is for displaying peripheral hexes
		self.is_visible = is_visible

class HiveBoard(object):
	""" A grid of hex tiles. Since insects can be placed forever in any direction,
		this will have to grow in a strange way, this is a TODO. """
	def __init__(self, size=7):
		# Row coordinates are backwards: y axis, x axis. Best to use an accessor
		self.rows = []
		for i in range(size):
			row = []
			for j in range(size):
				row.append(Hex((j, i)))
			self.rows.append(row)

		# TODO math.ceil
		self.rows[3][3] = Hex((3, 3), is_visible=True)
		self.start = self.rows[3][3]
	
	def _id_to_coord(self, id):
		return map(int, id.split('-'))

	def get_all(self):
		result = []
		for row in self.rows:
			result.extend(row)
		return result

	def get_by_coord(self, coord):
		return self.rows[coord[1]][coord[0]]

	def get_by_id(self, hex_id):
		coord = self._id_to_coord(hex_id)
		return self.get_by_coord(coord)
	
	def get_insects_by_id(self, hex_id):
		return self.get_by_id(hex_id).insects

	def neighbors(self, hex_id):
		coord = self._id_to_coord(hex_id)
		offsets =  [(-1, -1), (0, -1), (1, -1),
					(-1, 0), (0, 1), (1, 0)]
		# Build a list of all the hexes offset from the target
		return [self.get_by_coord((coord[0] + x, coord[1] + y)) for x, y in offsets]
		

class GameState(object):
	""" Everything we need to store and successfully resume a game. """
	def __init__(self, white_player, black_player):
		self.white_player = white_player
		self.black_player = black_player
		self.current_turn = 0

		# FIXME: sigh...so verbose and redundant
		self.white_pieces = Spider("white"), Spider("white"), Beetle("white"), Beetle("white"), Grasshopper("white"), Grasshopper("white"),Grasshopper("white"), Bee("white"), Ant("white"), Ant("white"), Ant("white")
		self.black_pieces = Spider("black"), Spider("black"), Beetle("black"), Beetle("black"), Grasshopper("black"), Grasshopper("black"),Grasshopper("black"), Bee("black"), Ant("black"), Ant("black"), Ant("black")
		self.board = HiveBoard()

		# Set the first time the game state is written to the store
		self.key = None
	
	def lookup_insect(self, color, name, current_hex_id=None):
		""" Given an insect's color, name, and current hex id return a reference to that insect. """
		for insect in (self.white_pieces + self.black_pieces):
			if insect.color == color and insect.name == name and insect.hex_id == current_hex_id:
				return insect
		else:
			return None

	def show_placements(self, color):
		""" Returns a list of hex ids that the player can play a new insect on """
		return [a_hex for a_hex in self.board.get_all() if a_hex.is_visible]

	def placement(self, color, insect_name, target_hex_id):
		""" TODO: this logic is duplicated, but it's a placeholder currently. """
		insect = self.lookup_insect(color, insect_name)
		target_hex = self.board.get_by_id(target_hex_id)

		# Tell the insect where it now is
		insect.hex_id = target_hex.id
		# Tell the hex what's on it
		target_hex.insects.append(insect)

		self.current_turn += 1

		# TODO: need actual logic here, this is placeholder
		newly_visible = self.board.neighbors(target_hex_id)

		for a_hex in newly_visible:
			a_hex.is_visible = True
		no_longer_visible = []
		return {
			'newly_visible': newly_visible,
			'no_longer_visible': no_longer_visible,
		}

	def show_moves(self, current_hex):
		""" Returns a list of hex ids that the insect on the current_hex can move to """
		return [a_hex for a_hex in self.board.get_all() if a_hex.is_visible]

	def _check_move(self, color, insect, current_hex_id, target_hex_id):
		""" Returns True if the insect can move to the target. """
		return True

	def move(self, current_hex_id, target_hex_id):
		""" Move a piece somewhere, throw an exception if it's not allowed. """
		target_hex = self.board.get_by_id(target_hex_id)
		current_hex = self.board.get_by_id(current_hex_id)
		insect = current_hex.insects[0]

		# Move the insect from its old spot
		current_hex.insects.remove(insect)
		# Tell the insect where it now is
		insect.hex_id = target_hex.id
		# Tell the hex what's on it
		target_hex.insects.append(insect)

		self.current_turn += 1

		# TODO: need actual logic here, this is placeholder
		newly_visible = self.board.neighbors(target_hex_id)

		for a_hex in newly_visible:
			a_hex.is_visible = True
		no_longer_visible = []
		return {
			'newly_visible': newly_visible,
			'no_longer_visible': no_longer_visible,
			'insect': insect
		}
		
	def winner(self):
		""" Returns None if the game is not over or the color of the winning player. """
		pass
