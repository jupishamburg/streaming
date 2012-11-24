# coding: utf-8

import streaminterface
import wsgiref.simple_server
import json

try:
	with open("streaminterface.conf") as f:
		streaminterface.bottle_app.config.update(json.load(f))
except IOError:
	pass

httpd = wsgiref.simple_server.make_server('127.0.0.1', 8080, streaminterface.app)
print("Serving HTTP on 127.0.0.1:8080...")

httpd.serve_forever()

