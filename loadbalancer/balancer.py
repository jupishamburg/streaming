#!/usr/bin/env python3
import bottle
from bottle import run, response, redirect, template, abort
from pprint import pprint
import urllib.request
import urllib.parse
import json
import time
import functools
import threading
import time
 
# stats refresher thread
class FetchStatsThread(threading.Thread):
	daemon = True
	interval = 10
 
	def __init__(self, servers, app=None):
		threading.Thread.__init__(self)
		self.servers = servers
		self.app = app
	
	def run(self):
		self.stats = {}

		while True:
			for url, config in self.servers.items():
				try:
					with urllib.request.urlopen(urllib.parse.urljoin(url, "/json.xsl")) as f:
						ic2_stats = json.loads(f.read().decode())
				except:
					del self.stats[url]
					continue

				# Prepare stats dictionary
				stats = {
					"max_listeners": config["max_listeners"],
					"current_listeners": 0,
					"mounts": {}
				}

				# Iterate through presented mount points
				for mount in ic2_stats["mounts"]:
					# Build mount point name and prefix it if requested
					mount_name = mount["mount"]
					if "prefix" in config:
						mount_name = config["prefix"] + mount_name

					# Add mount point to stats dictionary
					stats["mounts"][mount_name] = {
						"title": mount["title"],
						"description": mount["description"],
						"genre": mount["genre"],
						"url": mount["url"],
						"bitrate": int(mount["bitrate"]),
						"listeners": int(mount["listeners"]),
					}

				if stats["mounts"]:
					# Calculate current listeners by adding listeners of all mount points together
					stats["current_listeners"] = functools.reduce(
						lambda a, b: a + b,
						map(lambda c: c["listeners"], stats["mounts"].values())
					)
				# Calculate free slots
				stats["free_slots"] = stats["max_listeners"] - stats["current_listeners"]
				# Calculate simple usage rate by dividing current listeners by max listeners
				stats["usage_rate"] = stats["current_listeners"] / stats["max_listeners"]
				# Add last refresh time
				stats["last_refresh"] = time.time()

				# Publish stats dictionary
				self.stats[url] = stats

			# Sleep for n seconds
			time.sleep(self.interval)

app = bottle.Bottle()

def find_mount_servers(servers, mount):
	# Fix mount point name if needed
	if mount[0] != "/":
		mount = "/" + mount
	# Sort server list by usage rate (lowest usage rate => first server)
	servers = sorted(
		servers,
		key=lambda s: s[1]["usage_rate"]
	)
	# Filter servers out which are full
	servers = filter(
		lambda s: s[1]["usage_rate"] < 1,
		servers
	)
	# Filter servers which can deliver the requested mount point
	servers = filter(
		lambda s: mount in s[1]["mounts"],
		servers
	)
	# Return result as list
	return list(servers)

def get_mounts(servers):
	mounts = {}
	for url, server in servers.items():
		for mount, mount_stats in server["mounts"].items():
			if mount not in mounts:
				mounts[mount] = {
					"servers": [],
					"listeners": 0,
					"title": mount_stats["title"],
					"description": mount_stats["description"],
					"genre": mount_stats["genre"],
					"bitrate": mount_stats["bitrate"],
					"url": mount_stats["url"]
				}
			mounts[mount]["servers"].append(url)
			mounts[mount]["listeners"] += mount_stats["listeners"]
	
	return mounts

@app.route("/<mount>.m3u")
def playlist(mount):
	servers = find_mount_servers(app.config["fetcher"].stats.items(), mount)

	if not servers:
		abort(404, "Uuuh … ooh … what about trying to listen to an existing stream?")

	urls = []

	# Iterate through the servers
	for url, server in servers:
		urls.append(urllib.parse.urljoin(url, mount))
	
	response.headers["Content-Type"] = "audio/x-mpegurl"
	return "\n".join(urls)

@app.route("/<mount>")
def redirector(mount):
	servers = find_mount_servers(app.config["fetcher"].stats.items(), mount)

	if not servers:
		# The requested mount point cannot be delivered
		abort(404, "Uuuh … ooh … what about trying to listen to an existing stream?")
	
	# Build url and redirect
	url, server = servers[0]
	redirect(urllib.parse.urljoin(url, mount), code=307)

@app.route("/stats.json")
def stats():
	response.headers["Content-Type"] = "application/json"
	return json.dumps(app.config["fetcher"].stats, indent=4)

@app.route("/config.json")
def config():
	response.headers["Content-Type"] = "application/json"
	return json.dumps(app.config["config"])

@app.route("/mounts.json")
def config():
	mounts = get_mounts(app.config["fetcher"].stats)
	
	response.headers["Content-Type"] = "applicationijson"
	return json.dumps(mounts, indent=4)

@app.route("/")
def index():
	servers = sorted(
		app.config["fetcher"].stats.items(),
		key=lambda s: s[1]["usage_rate"]
	)
	mounts = get_mounts(app.config["fetcher"].stats)

	total_listeners = functools.reduce(
		lambda a, b: a + b,
		map(
			lambda s: s[1]["current_listeners"],
			servers
		)
	)

	return template("index.tpl", servers=servers, total_listeners=total_listeners, mounts=mounts)

if __name__ == '__main__':
	import argparse
	argparser = argparse.ArgumentParser(description="Load balancer for Icecast2 streams")
	argparser.add_argument('-c', '--config', type=open, default="balancer.json")
	argparser.add_argument('-S', '--slave', default=None)
	argparser.add_argument('-s', '--server', type=str, default="tornado")
	argparser.add_argument('-H', '--host', type=str, default="0.0.0.0")
	argparser.add_argument('-p', '--port', type=int, default=8080)
	args = argparser.parse_args()

	if args.slave:
		with urllib.request.urlopen(args.slave) as f:
			config = json.loads(f.read().decode())
	else:
		config = json.load(args.config)
	fetcher = FetchStatsThread(config)
	fetcher.start()

	app.config["config"] = config
	app.config["fetcher"] = fetcher
	run(app, server=args.server, host=args.host, port=args.port)

