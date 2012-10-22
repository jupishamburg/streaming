#!/usr/bin/env python3
import bottle
from bottle import run, response, redirect, template, abort
from operator import itemgetter
import urllib.request
import json
import time
import threading
 
# stats refresher thread
class FreeSlotThread(threading.Thread):
	daemon = True
 
	def __init__(self, config, app):
		threading.Thread.__init__(self)
		self.config = config
		self.app = app
 
	def run(self):
		master = None
		masters = 0
	
		# find the master
		for server in self.config["servers"]:
			if server["master"] == True:
				master = server
				masters += 1
		if masters == 0 or masters > 1:
			exit("Error: There are {0} master(s).".format(masters))

		while True:
			# listener slots & mountpoints per server
			for server in self.config["servers"]:
				url = "http://{0}/json.xsl".format(server["url"])
				stats = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
				server["current-listeners"] = int(stats["total_listeners"])
				server["free-slots"] = server["max-listeners"] - int(stats["total_listeners"])
				
				# get the mountpoints
				server["mounts"] = []
				for mount in stats["mounts"]:
					server["mounts"].append(mount["mount"][1:len(mount["mount"])])
			
			# get the available mountpoints (available as in: distributed by the master, reachable over all servers)
			self.config["mountpoints"] = master["mounts"]
			for mount in self.config["mountpoints"]:
				for server in self.config["servers"]:
					if mount not in server["mounts"]:
						self.config["mountpoints"].remove(mount)
			
			# update the bottlepy config
			self.app.config.update(self.config)
 
			time.sleep(self.config["update-interval"])

app = bottle.Bottle()

# playlist deliver
@app.route("/<mount>.m3u")
def playlist(mount):
	if mount not in app.config["mountpoints"]:
		abort(404, "Uuuh … ooh … what about trying to listen to an existing stream?")
		
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
	if mount not in app.config["mountpoints"]:
		abort(404, "Uuuh … ooh … what about trying to listen to an existing stream?")
		
	s = sorted(app.config["servers"], key=itemgetter("free-slots"), reverse=True)[0]
	url = "http://{0}/{1}".format(
		s["url"],
		mount
	)

	redirect(url, code=307)
 
# stats deliver
@app.route("/")
def stats():
	servers = sorted(app.config["servers"], key=itemgetter("free-slots"), reverse=True)
	
	return template("index.tpl", servers=servers)

if __name__ == '__main__':
	import argparse
	argparser = argparse.ArgumentParser(description="Load balancer for Icecast2 streams")
	argparser.add_argument('-c', '--config', type=open, default="balancer.json")
	argparser.add_argument('-s', '--server', type=str, default="tornado")
	argparser.add_argument('-H', '--host', type=str, default="0.0.0.0")
	argparser.add_argument('-p', '--port', type=int, default=8080)
	args = argparser.parse_args()

	config = json.load(args.config)
	FreeSlotThread(config, app).start()

	app.config.update(config)
	run(app, server=args.server, host=args.host, port=args.port)
 
