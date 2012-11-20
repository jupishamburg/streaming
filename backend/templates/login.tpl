<form action="/login" method="post">
	<dl>
		<dt><label for="username">Username</label></dt>
		<dd><input type="text" name="username" id="username" /></dd>

		<dt><label for="password">Password</label></dt>
		<dd><input type="password" name="password" id="password" /></dd>
	</dl>
	<input type="submit" value="Do this …" />
</form>

%rebase templates/layout title="Login"