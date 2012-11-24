# coding: utf-8
# Some kind of Py3k compatible session middleware
# Highly professional source code which should be open sourced

import os
import hashlib
import http.cookies
Cookie = http.cookies

class Session(dict):
	""" Simple dict with an attached id and the information about persistance """

	# Session ID
	id = None
	persistent = False

	def __init__(self, _data=None, id=None):
		if _data is not None:
			dict.update(self, _data)

		if id is not None:
			self.id = id
		else:
			self.id = self._generate_id()

	def __repr__(self):
		if self.persistent:
			return "<session [persistent] {0}: {1}>".format(self.id, dict.__repr__(self))
		return "<session {0}: {1}>".format(self.id, dict.__repr__(self))

	def __nonzero__(self):
		return bool(dict.__len__(self)) or bool(self.persistent)

	@staticmethod
	def _generate_id():
		return hashlib.md5(os.urandom(64)).hexdigest()

class SessionMiddleware(object):
	""" This is a WSGI compilant middleware, which implements simple sessions
	for your WSGI application. It uses external objects to provide storage logic.

	Usage:

		# app is a WSGI middleware
		# persistence is a dict-alike object
		app = SessionMiddleware(app, persistence=persistence)
	"""

	session_cookie = "SESSID"
	app = None
	persistence = None

	def __init__(self, _dict=None, **kwargs):
		if _dict is not None:
			self.__dict__.update(_dict)
		self.__dict__.update(kwargs)

	def __call__(self, environ, start_response):
		# Spaghetti!
		# XXX This works with much magic! Don't touch this, you cannot understand this code!
		session = None

		reqcookie = Cookie.SimpleCookie(environ.get("HTTP_COOKIE", ""))
		session_id = None
		if self.session_cookie in reqcookie:
			session_id = reqcookie[self.session_cookie].value
		del reqcookie

		if session_id and session_id in self.persistence:
			session = Session(self.persistence[session_id], session_id)
			session.persistent = True
		del session_id
		
		if session is None:
			session = Session()
		
		def _start_response(status, header):
			#	Hahaha! It's not our problem if your HTTP parser uses dictionaries!
			cookie = Cookie.SimpleCookie()
			cookie[self.session_cookie] = session.id
			# FIXME Dirty hack
			header.append(tuple(str(cookie).split(": ", 1)))

			return start_response(status, header)

		environ["mergee.session"] = session
		# For bottle compatibility
		environ["bottle.request.ext.session"] = session

		out = self.app(environ, _start_response)

		if session:
			self.persistence[session.id] = session

		return out

