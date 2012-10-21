%totallisteners = 0

<!DOCTYPE html>
<html>
	<head>
		<title>Streaming load balancer</title>
		<meta charset="utf-8" />
	</head>
	<body>
		<table border="1">
			<tr>
				<th>Host</th>
				<th>Listeners</th>
				<th>Free slots</th>
				<th>Total slots</th>
			</tr>
			%for s in servers:
				<tr>
					<td><a href="http://{{ s["url"] }}">{{ s["url"] }}</a></td>
					<td>{{ s["current-listeners"] }}</td>
					<td>{{ s["free-slots"] }}</td>
					<td>{{ s["max-listeners"] }}</td>
				</tr>
				
				%totallisteners += s["current-listeners"]
			%end
		</table>
		<p>Total listeners: {{ totallisteners }}</p>
	</body>
</html>
