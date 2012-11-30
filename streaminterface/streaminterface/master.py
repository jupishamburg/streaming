# coding: utf-8

import bottle
import urllib.parse
import threading
from bottle import request, redirect, response

class RequireKeyMiddleware(object):
	def __init__(self, backend, key=None):
		self.backend = backend
		self.key = key
	
	def __call__(self, environ, start_response):
		if self.key:
			try:
				query_string = environ["QUERY_STRING"]
				query = urllib.parse.parse_qs(query_string)

				if query.get("key", [None])[0] != self.key:
					start_response("403 Forbidden", [('Content-Type', 'text/plain')])
					return [b"Forbidden\n"]
			except KeyError:
				pass

		return self.backend(environ, start_response)

class SaveConfigThread(threading.Thread):
	daemon = True

	def __init__(self, config, file, interval=30):
		threading.Thread.__init__(self)
		self.config = config
		self.file = file
		self.interval = interval
	
	def run():
		while True:
			with open(self.file, "w") as f:
				json.dump(self.config, f, indent=2)
			time.sleep(self.interval)

bottle_app = app = bottle.Bottle()
app.config.update({
	"key": None,
	"streams": {}
})

@app.route("/")
def index():
	return "{}"

@app.route("/streams", "GET")
def list_streams():
	pass

@app.route("/streams", "POST")
def create_stream():
	pass

@app.route("/streams/<stream>", "GET")
def show_stream(stream):
	pass

@app.route("/streams/<stream>", "DELETE")
def delete_stream(stream):
	pass

if __name__ == '__main__':
	import json
	import argparse
	import wsgiref.simple_server

	argparser = argparse.ArgumentParser(description='Simple stream server master')
	argparser.add_argument('-H', '--host', default='127.0.0.1', help='IP address to bind')
	argparser.add_argument('-p', '--port', default=42023, type=int, help='Port number to bind')
	argparser.add_argument('-c', '--config', default='streammaster.conf', help='JSON configuration file')

	args = argparser.parse_args()

	try:
		with open(args.config) as f:
			app.config.update(json.load(f))
	except IOError:
		pass

	if app.config.get('key'):
		app = RequireKeyMiddleware(app, app.config.get('key'))
	
	httpd = wsgiref.simple_server.make_server(args.host, args.port, app)
	print("Serving HTTP on {host}:{port}...".format(host=args.host, port=args.port))

	httpd.serve_forever()

