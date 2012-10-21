#!/usr/bin/env python
from bottle import route, run, response, redirect
from operator import itemgetter
import urllib.request
import json
import time
import threading
 
config = {
	"servers": [
		{
			"url": "gododdin.techel.net:8000",
			"max-listeners": 100,
			"current-listeners": 0,
			"free-slots": 100
		},
		{
			"url": "cexy.techel.net:8000",
			"max-listeners": 100,
			"current-listeners": 0,
			"free-slots": 100
		}
	],
	"update-interval": 15,

	"webserver": {
		"host": "0.0.0.0",
		"port": 8080,
		"frontend": "tornado"
	}
}
 
# stats refresher thread
class FreeSlotThread(threading.Thread):
	daemon = True
 
	def __init__(self):
		threading.Thread.__init__(self)
 
	def run(self):
		while True:
			for server in config["servers"]:
				url = "http://{0}/json.xsl".format(server["url"])
				stats = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
				server["current-listeners"] = int(stats["total_listeners"])
				server["free-slots"] = server["max-listeners"] - int(stats["total_listeners"])
 
			time.sleep(config["update-interval"])
 
# playlist deliver
@route("/<mount>.m3u")
def playlist(mount):
	urls = []
	servers = sorted(config["servers"], key=itemgetter("free-slots"), reverse=True)
	for s in servers:
		urls.append("http://{0}/{1}".format(
			s["url"],
			mount
		))
 
	response.headers["Content-Type"] = "audio/x-mpegurl"
	return "\n".join(urls)

# redirect deliver (for html5 audio players, …)
@route("/<mount>")
def redirector(mount):
	s = sorted(config["servers"], key=itemgetter("free-slots"), reverse=True)[0]
	url = "http://{0}/{1}".format(
		s["url"],
		mount
	)

	redirect(url, code=307)
 
# stats deliver
@route("/")
def stats():
	out = '<table border="1"><tr><th>Listeners</th><th>Slots</th><th>Free slots</th><th>Server</th></tr>'
	servers = sorted(config["servers"], key=itemgetter("free-slots"), reverse=True)
	for s in servers:
		out += '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td><a href="http://{3}">{3}</a></td></tr>'.format(
			s["current-listeners"],
			s["max-listeners"],
			s["free-slots"],
			s["url"]
		)
 
	out += '</table>'
	return out
 
# run the thread
stats = FreeSlotThread()
stats.start()
 
# run the http server
run(server=config["webserver"]["frontend"], host=config["webserver"]["host"], port=config["webserver"]["port"])
