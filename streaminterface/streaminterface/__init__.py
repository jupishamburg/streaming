# coding: utf-8

import streaminterface.session
import bottle
import functools
import jinja2
import os.path
from bottle import request, redirect

jinja2_env = jinja2.Environment(loader=jinja2.PackageLoader("streaminterface", "templates"))

sessions = {}
bottle_app = app = bottle.Bottle()

def render_template(_tpl, **kwargs):
	tpl = jinja2_env.get_template(_tpl)
	return tpl.render(kwargs)

def force_login(func):
	""" Function decorator which forces login on a Bottle route """
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		if not request.session.get("user"):
			request.session["redirect_after_login"] = request.url
			redirect("/login")
		return func(*args, **kwargs)
	return wrapper

# routes
@app.route("/", "GET")
def index():
	if "user" in request.session:
		redirect("/streams")
	return render_template("login.html")

@app.route("/login", "POST")
def login():
	try:
		user, password = request.forms["username"], request.forms["password"]
	except KeyError:
		redirect("/")
	users = request.app.config["users"]
	if user not in users:
		redirect("/")
	if users[user] != password:
		redirect("/")

	request.session["user"] = user
	redirect("/")

@app.route("/logout", "GET")
def logout():
	del request.session["user"]
	redirect("/")

@app.route("/streams", "GET")
@force_login
def streams():
	return render_template("streams.html", streams=[])

@app.route("/streams", "POST")
@force_login
def streams_create():
	pass

@app.route("/streams/new", "GET")
@force_login
def streams_new():
	return render_template("streams_new.html")

@app.route("/streams/<stream>", "GET")
@force_login
def streams_get(stream):
	return render_template("streams_get.html")

@app.route("/streams/<stream>", "DELETE")
@app.route("/streams/<stream>/delete", "ANY")
@force_login
def streams_delete(stream):
	pass

app = streaminterface.session.SessionMiddleware(app=app, persistence=sessions)

