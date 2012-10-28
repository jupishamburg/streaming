<!DOCTYPE html>
<html>
	<head>
		<title>Streaming load balancer</title>
		<meta charset="utf-8" />
	</head>
	<body>
		<table border="1">
			<tr>
				<th>Mount</th>
				<th>Title</th>
				<th>Description</th>
				<th>Listeners</th>
			</tr>
			%for name, mount in mounts.items():
				<tr>
					<td><a href="{{ name }}">{{ name }}</a></td>
					<td>{{ mount["title"] }}</td>
					<td>{{ mount["description"] }}</td>
					<td>{{ mount["listeners"] }}</td>
				</tr>
			%end
		</table>
		<table border="1">
			<tr>
				<th>Host</th>
				<th>Listeners</th>
				<th>Free slots</th>
				<th>Total slots</th>
			</tr>
			%for url, server in servers:
				<tr>
					<td><a href="{{ url }}">{{ url }}</a></td>
					<td>{{ server["current_listeners"] }}</td>
					<td>{{ server["free_slots"] }}</td>
					<td>{{ server["max_listeners"] }}</td>
				</tr>
			%end
		</table>
		<p>Total listeners: {{ total_listeners }}</p>
	</body>
</html>
