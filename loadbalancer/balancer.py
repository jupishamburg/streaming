#!/usr/bin/env python
import bottle
from bottle import run, response, redirect
from operator import itemgetter
import urllib.request
import json
import time
import threading
 
# stats refresher thread
class FreeSlotThread(threading.Thread):
	daemon = True
 
	def __init__(self, config):
		threading.Thread.__init__(self)
		self.config = config
 
	def run(self):
		while True:
			for server in self.config["servers"]:
				url = "http://{0}/json.xsl".format(server["url"])
				stats = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
				server["current-listeners"] = int(stats["total_listeners"])
				server["free-slots"] = server["max-listeners"] - int(stats["total_listeners"])
 
			time.sleep(self.config["update-interval"])

app = bottle.Bottle()

# playlist deliver
@app.route("/<mount>.m3u")
def playlist(mount):
	urls = []
	servers = sorted(app.config["servers"], key=itemgetter("free-slots"), reverse=True)
	for s in servers:
		urls.append("http://{0}/{1}".format(
			s["url"],
			mount
		))
 
	response.headers["Content-Type"] = "audio/x-mpegurl"
	return "\n".join(urls)

# redirect deliver (for html5 audio players, …)
@app.route("/<mount>")
def redirector(mount):
	s = sorted(app.config["servers"], key=itemgetter("free-slots"), reverse=True)[0]
	url = "http://{0}/{1}".format(
		s["url"],
		mount
	)

	redirect(url, code=307)
 
# stats deliver
@app.route("/")
def stats():
	out = '<table border="1"><tr><th>Listeners</th><th>Slots</th><th>Free slots</th><th>Server</th></tr>'
	servers = sorted(app.config["servers"], key=itemgetter("free-slots"), reverse=True)
	for s in servers:
		out += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td><a href="http://{3}">{3}</a></td></tr>'.format(
			s["current-listeners"],
			s["max-listeners"],
			s["free-slots"],
			s["url"]
		)
 
	out += '</table>'
	return out

if __name__ == '__main__':
	import argparse
	argparser = argparse.ArgumentParser(description="Load balancer for Icecast2 streams")
	argparser.add_argument('-c', '--config', type=open, default="balancer.json")
	argparser.add_argument('-s', '--server', type=str, default="tornado")
	argparser.add_argument('-H', '--host', type=str, default="0.0.0.0")
	argparser.add_argument('-p', '--port', type=int, default=8080)
	args = argparser.parse_args()

	config = json.load(args.config)
	FreeSlotThread(config).start()

	app.config.update(config)
	run(app, server=args.server, host=args.host, port=args.port)
 
