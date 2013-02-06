#!/usr/bin/liquidsoap
set("log.file.path", "/var/log/liquidsoap/fallback.log")
set("log.level", 3)
set("init.daemon.pidfile.path", "/var/run/liquidsoap/fallback.pid")
set("server.telnet", true)
set("server.telnet.port", 8001)
set("harbor.bind_addr", "0.0.0.0")

fallback_file = "/etc/liquidsoap/problems.ogg"
fallback_stream = "http://localhost:8000/fallback.ogg"

output_name	= "Junge Piraten Live vor dem Mikrofon"
output_desc	= "Trollerei und anzügliche Bemerkungen"
output_url	= "http://ragefac.es/61"
output_genre	= "Trollfunk"
output_amplify	= 1.5

ice_host	= "aluminium.grimpen.net"
ice_user	= "source"
ice_port	= 8000
ice_password	= "***"
ice_mount	= "listen"
ice_public	= true

harbor_port	= 8080
harbor_password	= "***"
harbor_mount	= "live"
harbor_amplify	= 1.0

fallback1	= amplify(1.2, input.http(fallback_stream))
# the following line is a workaround which removes annoying buffer overflow log messages. these messages aren't harmful but they are really annoying. http://permalink.gmane.org/gmane.comp.audio.liquidsoap.user/1297
output.dummy(mksafe(fallback1))
fallback2	= amplify(1.0, single(fallback_file))

def crossfade(a,b)
	add(normalize = false,
		[fade.initial(duration=2., b),
			sequence(merge=true, 
				[blank(duration=0.), fallback([])]),
		fade.final(duration=2., a)])
end

live = input.harbor(harbor_mount, port = harbor_port, password = harbor_password)
# i herd u no liek silence so i inserted teh following line
live = strip_blank(threshold = -39., length = 20., live)
live = amplify(harbor_amplify, live)
# i no need metadata. noar do u?
output = drop_metadata(output)

output = audio_to_stereo( 
		amplify(output_amplify, 
			fallback(track_sensitive = false, transitions = [crossfade, crossfade], [live, fallback1, mksafe(fallback2)])
		)
	)

output.icecast(%mp3(bitrate = 64), host = ice_host, port = ice_port, icy_metadata = "true",
	password = ice_password, mount = string.concat([ice_mount, ".mp3"]), user = ice_user, public = ice_public,
	name = output_name, description = output_desc,
	genre = output_genre, url = output_url,
	output)

output.icecast(%vorbis.cbr(bitrate = 56), host = ice_host, port = ice_port, icy_metadata = "true",
	password = ice_password, mount = string.concat([ice_mount, ".ogg"]), user = ice_user, public = ice_public,
	name = output_name, description = output_desc,
	genre = output_genre, url = output_url,
	output)
