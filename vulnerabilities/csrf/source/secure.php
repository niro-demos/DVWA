<?php

if( isset( $_POST['Change'] ) ) {
	checkToken( $_POST['user_token'] ?? '', $_SESSION['session_token'], 'index.php' );
	$pass_curr = md5( stripslashes( $_POST['password_current'] ?? '' ) );
	$pass_new = $_POST['password_new'] ?? '';
	$pass_conf = $_POST['password_conf'] ?? '';
	$current_user = dvwaCurrentUser();
	$data = $db->prepare( 'SELECT password FROM users WHERE user = (:user) AND password = (:password) LIMIT 1;' );
	$data->bindParam( ':user', $current_user, PDO::PARAM_STR );
	$data->bindParam( ':password', $pass_curr, PDO::PARAM_STR );
	$data->execute();
	if( hash_equals( $pass_new, $pass_conf ) && $data->rowCount() == 1 ) {
		$password = md5( $pass_new );
		$data = $db->prepare( 'UPDATE users SET password = (:password) WHERE user = (:user);' );
		$data->bindParam( ':password', $password, PDO::PARAM_STR );
		$data->bindParam( ':user', $current_user, PDO::PARAM_STR );
		$data->execute();
		$html .= '<pre>Password Changed.</pre>';
	} else {
		$html .= '<pre>Passwords did not match or current password incorrect.</pre>';
	}
}

generateSessionToken();

?>
