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
	def __init__(self, coord, insect=None):
		self.coord = coord
		self.id = '%s-%s' % self.coord
		self.insects = []
		if insect is not None:
			self.insects.append(insect)

class HiveBoard(object):
	""" A grid of hex tiles. Since insects can be placed forever in any direction,
		this will have to grow in a strange way, this is a TODO. """
	def __init__(self, start_coord):
		self.hexes = [Hex((start_coord[0], start_coord[1]))]
	
	def add_by_id(self, hex_id, insect=None):
		if self.get_by_id(hex_id):
			# TODO: exception type
			raise Exception
		a_hex = Hex(self._id_to_coord(hex_id), insect=insect)
		self.hexes.append(a_hex)
		return a_hex
		
	def all_ids(self):
		return [a_hex.id for a_hex in self.hexes]

	def is_visible(self, hex_id):
		a_hex = self.get_by_id(hex_id)
		return len(self.vacant_neighbor_ids(hex_id)) < 6 or a_hex and a_hex.insects

	def all_visible_ids(self):
		return [hex_id for hex_id in self.all_ids() if self.is_visible(hex_id)]

	def get_by_id(self, hex_id):
		for a_hex in self.hexes:
			if a_hex.id == hex_id:
				return a_hex
		else:
			return None
	
	def get_insects_by_id(self, hex_id):
		return self.get_by_id(hex_id).insects

	def vacant_neighbor_ids(self, hex_id):
		result =[]
		for neighbor_id in self.neighbor_ids(hex_id):
			a_hex = self.get_by_id(neighbor_id)
			if not a_hex or not a_hex.insects:
				result.append(neighbor_id)

		return result

	def neighbor_ids(self, hex_id):
		" Return the ids of all the hexes adjacent to the hex_id. """
		coord = self._id_to_coord(hex_id)
		if coord[1] % 2 == 0:
			offsets =  [(0, -1), (-1, 0), (0, 1),
						(1, -1), (1, 0), (1, 1)]
		else:
			offsets =  [(-1, -1), (-1, 0), (-1, 1),
						(0, -1), (1, 0), (0, 1)]
		# Build a list of all the hex ids offset from the target
		return ['%s-%s' % (coord[0] + x, coord[1] + y) for x, y in offsets]
		
	def _id_to_coord(self, id):
		return tuple(map(int, id.split('-')))


class GameState(object):
	""" Everything we need to store and successfully resume a game. """
	def __init__(self, white_player, black_player):
		self.white_player = white_player
		self.black_player = black_player
		self.current_turn = 0

		# FIXME: sigh...so verbose and redundant
		self.white_pieces = Spider("white"), Spider("white"), Beetle("white"), Beetle("white"), Grasshopper("white"), Grasshopper("white"),Grasshopper("white"), Bee("white"), Ant("white"), Ant("white"), Ant("white")
		self.black_pieces = Spider("black"), Spider("black"), Beetle("black"), Beetle("black"), Grasshopper("black"), Grasshopper("black"),Grasshopper("black"), Bee("black"), Ant("black"), Ant("black"), Ant("black")
		self.board = HiveBoard(start_coord=(3, 3))

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
		if self.current_turn == 0:
			return [self.board.hexes[0].id]
		else:
			potential_placements = []
			for insect in (self.white_pieces + self.black_pieces):
				if insect.hex_id is not None:
					potential_placements.extend(self.board.vacant_neighbor_ids(insect.hex_id))
			return [hex_id for hex_id in (set(potential_placements))]


	def placement(self, color, insect_name, target_hex_id):
		""" TODO: this logic is duplicated, but it's a placeholder currently. """
		insect = self.lookup_insect(color, insect_name)
		target_hex = self.board.get_by_id(target_hex_id) or self.board.add_by_id(target_hex_id)

		# Tell the insect where it now is
		insect.hex_id = target_hex.id
		# Tell the hex what's on it
		target_hex.insects.append(insect)

		self.current_turn += 1

		# TODO: need actual logic here, this is placeholder
		newly_visible = self.board.vacant_neighbor_ids(target_hex_id)
		no_longer_visible = []
		return {
			'newly_visible': newly_visible,
			'no_longer_visible': no_longer_visible,
		}

	def show_moves(self, current_hex):
		""" Returns a list of hex ids that the insect on the current_hex can move to """
		return self.board.all_visible_ids() + self.board.vacant_neighbor_ids(current_hex)

	def _check_move(self, color, insect, current_hex_id, target_hex_id):
		""" Returns True if the insect can move to the target. """
		return True

	def move(self, current_hex_id, target_hex_id):
		""" Move a piece somewhere, throw an exception if it's not allowed. """
		current_hex = self.board.get_by_id(current_hex_id)
		target_hex = self.board.get_by_id(target_hex_id) or self.board.add_by_id(target_hex_id)
		insect = current_hex.insects[0]

		# Move the insect from its old spot
		current_hex.insects.remove(insect)
		# Tell the insect where it now is
		insect.hex_id = target_hex.id
		# Tell the hex what's on it
		target_hex.insects.append(insect)

		self.current_turn += 1

		newly_visible = self.board.vacant_neighbor_ids(target_hex_id)
		no_longer_visible = list(set(self.board.all_ids()) - set(self.board.all_visible_ids()))
		return {
			'newly_visible': newly_visible,
			'no_longer_visible': no_longer_visible,
			'insect': insect
		}
		
	def winner(self):
		""" Returns None if the game is not over or the color of the winning player. """
		pass
