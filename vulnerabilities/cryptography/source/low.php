<?php

$errors = "";
$success = "";
$password_hash = '$2y$10$EbZ76By6/9nFIWqkAWimnuvSOf.mRBrxKFRcnBqLwKSJH8jqYoZji';

if ($_SERVER['REQUEST_METHOD'] == "POST") {
	try {
		if (array_key_exists ('password', $_POST)) {
			$password = $_POST['password'];
			if (password_verify($password, $password_hash)) {
				$success = "Welcome back user";
			} else {
				$errors = "Login Failed";
			}
		}
	} catch(Exception $e) {
		$errors = $e->getMessage();
	}
}

$html = '<p>Enter the account password to continue.</p>';

if ($errors != "") {
	$html .= '<div class="warning">' . $errors . '</div>';
}

if ($success != "") {
	$html .= '<div class="success">' . $success . '</div>';
}

$html .= "
		<form name=\"ecb\" method='post' action=\"" . $_SERVER['PHP_SELF'] . "\">
			<p>
				<label for='password'>Password:</lable><br />
<input type='password' id='password' name='password'>
			</p>
			<p>
				<input type=\"submit\" value=\"Login\">
			</p>
		</form>
";
?>
