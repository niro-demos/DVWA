<?php

if( isset( $_GET[ 'Login' ] ) ) {
	// Get username
	$user = $_GET[ 'username' ];

	// Get password
	$pass = $_GET[ 'password' ];
	$pass = md5( $pass );

	// Bind credentials so quotes and SQL syntax remain data.
	try {
		$data = $db->prepare('SELECT * FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;');
		$data->bindValue(':user', $user, PDO::PARAM_STR);
		$data->bindValue(':password', $pass, PDO::PARAM_STR);
		$data->execute();
		$row = $data->fetch(PDO::FETCH_ASSOC);
	} catch (Throwable $error) {
		error_log($error->getMessage());
		$row = false;
	}

	if ($row !== false) {
		// Get users details
		$avatar = $row["avatar"];

		// Login successful
		$html .= "<p>Welcome to the password protected area {$user}</p>";
		$html .= "<img src=\"{$avatar}\" />";
	}
	else {
		// Login failed
		$html .= "<pre><br />Username and/or password incorrect.</pre>";
	}

	((is_null($___mysqli_res = mysqli_close($GLOBALS["___mysqli_ston"]))) ? false : $___mysqli_res);
}

?>
