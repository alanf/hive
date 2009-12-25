#!/usr/bin/env python
import cgi
import os
from django.utils import simplejson

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class Insect(object):
	pass

class Spider(Insect):
	name = 'spider'

class Beetle(Insect):
	name = 'beetle'

class Grasshopper(Insect):
	name = 'grasshopper'

class Bee(Insect):
	name = 'bee'

class Ant(Insect):
	name = 'ant'

class Hex(object):
	def __init__(self, coord, is_playable=False, current_insect=None, is_visible=False):
		self.coord = coord
		self.id = '%s-%s' % self.coord
		self.is_playable = is_playable
		self.current_insect = current_insect
		self.is_visible = is_visible

class HiveBoard(object):
	def __init__(self, size=7):
		self.rows = []
		for i in range(size):
			row = []
			# TODO: could make a list comp
			for j in range(size):
				row.append(Hex((j, i)))
			self.rows.append(row)

		# TODO math.ceil
		self.rows[3][3] = Hex((3, 3), is_playable=True, is_visible=True)
		self.start = self.rows[3][3]

class ShowMoves(webapp.RequestHandler):
	def get(self):
		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		response = {'hexes': ['3-3']}
		self.response.out.write(simplejson.dumps(response))
		
class Move(webapp.RequestHandler):
	def post(self):
		insect_name = self.request.get('insect_name')
		insect_color = self.request.get('insect_color')
		target_hex = self.request.get('target_hex')
		response = {
			'success': True,
			'reveal_hex_ids': ['2-3', '3-4', '4-3', '3-2', '2-2', '2-4']
		}
		self.response.out.write(simplejson.dumps(response))
		
class Game(webapp.RequestHandler):
	def get(self):
		template_values = {
			'board': HiveBoard(),
			# TODO: load game state
			'pieces': (Spider(), Beetle(), Grasshopper(), Bee(), Ant()),
		}
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		
application = webapp.WSGIApplication([
									('/', MainPage),
									('/index.html', Game),
									('/show_moves', ShowMoves),
									('/move', Move),
									],
                                    debug=True)
def main():
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()
