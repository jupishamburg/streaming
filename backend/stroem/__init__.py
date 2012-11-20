import bottle
from beaker.middleware import SessionMiddleware

b_app = bottle.Bottle()
app = SessionMiddleware(b_app, {
	'session.type': 'memory',
	'session.secret': 'oKuoc2eijeifahwe3uv5koo3Po4Een2thahL0phaech4iephai1Cheigh6Shohso'
})