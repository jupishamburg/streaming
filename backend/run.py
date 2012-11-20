#!/usr/bin/env python3
import bottle
import argparse
import json
from stroem import app

# config foobar
app.config = {
	"template_path": "templates/",
	"users": json.load(open("users.json", "r"))
}

# all the magic!
import stroem.userfoo

if __name__ == "__main__":
	# args foobar
	argparser = argparse.ArgumentParser(description="Configuration backend for the Young Pirates Streaming Platform")
	argparser.add_argument('-s', '--server', type=str, default="tornado")
	argparser.add_argument('-H', '--host', type=str, default="0.0.0.0")
	argparser.add_argument('-p', '--port', type=int, default=8080)
	args = argparser.parse_args()

	bottle.run(app, server=args.server, host=args.host, port=args.port)