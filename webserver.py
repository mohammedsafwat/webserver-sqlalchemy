from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from database_setup import Base, MenuItem, Restaurant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to db
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>"
					output += "Are you sure you want to delete "
					output += myRestaurantQuery.name
					output += "?"
					output += "</h1>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantIDPath
					output += "<input type='submit' value='Delete'>"
					output += '</form>'
					output += "</body></html>"
					self.wfile.write(output)

			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>"
					output += myRestaurantQuery.name
					output += "</h1>"
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurantIDPath
					output += "<input name='newRestaurantName' type='text' placeholder='%s'>" % myRestaurantQuery.name
					output += "<input type='submit' value='Rename'>"
					output += '</form>'
					output += "</body></html>"
					self.wfile.write(output)

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1>Make a new restaurant</h1>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
				output += "<input name='newRestaurantName' type='text' placeholder='New Restaurant Name'>"
				output += "<input type='submit' value='Create'>"
				output += '</form>'
				output += '</body></html>'
				self.wfile.write(output)

			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"
				for restaurant in restaurants:
					output += restaurant.name
					output += "</br>"
					output += "<a href='/restaurants/%s/edit'>Edit</a>" % restaurant.id
					output += "</br>"
					output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
					output += "</br>"
					output += "</br>"
				self.wfile.write(output)
				return

			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you like to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>&#161Hello <a href='/hello'>Back to hello!</a>"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you like to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
		except IOError:
			self.send_error(404, "File not found error %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

				if myRestaurantQuery != []:
					session.delete(myRestaurantQuery)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')	
					restaurantIDPath = self.path.split("/")[2]
					myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
					if myRestaurantQuery != []:
						myRestaurantQuery.name = messagecontent[0]
						session.add(myRestaurantQuery)
						session.commit()
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()

			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('newRestaurantName')

				# Create a new restaurant class
				newRestaurant = Restaurant(name = messagecontent[0])
				session.add(newRestaurant)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

				return

			# self.send_response(301)
			# self.send_header('Content-type', 'text/html')
			# self.end_headers()
			# # main value, dict parameters
			# # parses the html form header
			# ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
			# if ctype == 'multipart/form-data':
			# 	fields = cgi.parse_multipart(self.rfile, pdict)
			# 	messagecontent = fields.get('message')

			# output = ""
			# output += "<html><body>"
			# output += "<h2>OK, how about this?</h2>"
			# output += "<h1> %s </h1>" % messagecontent[0]
			# output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What do you like to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
			# output += "</body></html>"
			# self.wfile.write(output)
			# print output
		except:
			pass
def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stoppin web sever.."
		server.socket.close()

if __name__ == '__main__':
	main()