output.icecast(
	%vorbis,
	host="localhost",
	password="Begh3eibie2ya2eiwei1Aez7eibahghe7jeiW6giec",
	mount="/listen.ogg",
	fallible=true,
	add([
		fallback(track_sensitive=false, [
			input.http(id="source", "http://localhost:8000/source.ogg"),
			input.http(id="fallback", "http://localhost:8000/fallback.ogg"),
			single("fallback.ogg")
		])
	])
)

