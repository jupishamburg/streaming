import bottle
from stroem import app, b_app

@b_app.route('/')
def index():
	session = bottle.request.environ["beaker.session"]
	
	if "login" in session:
		return "wohoo \o/"

	return bottle.template("{0}/login.tpl".format(
		app.config["template_path"]
	))