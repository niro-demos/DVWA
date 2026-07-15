<?php
if( isset( $_POST['Change'] ) && ( $_POST['step'] ?? '' ) === '1' ) {
	$hide_form = true;
	$pass_new = $_POST['password_new'] ?? '';
	$pass_conf = $_POST['password_conf'] ?? '';
	$resp = recaptcha_check_answer( $_DVWA['recaptcha_private_key'], $_POST['g-recaptcha-response'] ?? '' );
	if( !$resp ) { $html .= '<pre>The CAPTCHA was incorrect.</pre>'; $hide_form = false; }
	elseif( !hash_equals( $pass_new, $pass_conf ) ) { $html .= '<pre>Both passwords must match.</pre>'; $hide_form = false; }
	else {
		$transaction = bin2hex( random_bytes( 32 ) );
		$_SESSION['captcha_change'] = array( 'id' => $transaction, 'password_digest' => hash( 'sha256', $pass_new ) );
		$password_html = htmlspecialchars( $pass_new, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8' );
		$html .= '<form action="#" method="POST"><input type="hidden" name="step" value="2" />'
			. '<input type="hidden" name="transaction" value="' . $transaction . '" />'
			. '<input type="hidden" name="password_new" value="' . $password_html . '" />'
			. '<input type="hidden" name="password_conf" value="' . $password_html . '" />'
			. '<input type="submit" name="Change" value="Change" /></form>';
	}
}
if( isset( $_POST['Change'] ) && ( $_POST['step'] ?? '' ) === '2' ) {
	$hide_form = true;
	$pass_new = $_POST['password_new'] ?? '';
	$pass_conf = $_POST['password_conf'] ?? '';
	$captcha_change = $_SESSION['captcha_change'] ?? null;
	$authorized = is_array( $captcha_change ) && hash_equals( $captcha_change['id'], $_POST['transaction'] ?? '' )
		&& hash_equals( $captcha_change['password_digest'], hash( 'sha256', $pass_new ) );
	unset( $_SESSION['captcha_change'] );
	if( !$authorized || !hash_equals( $pass_new, $pass_conf ) ) { $html .= '<pre>Password change confirmation was invalid or expired.</pre>'; $hide_form = false; return; }
	$password = md5( $pass_new );
	$current_user = dvwaCurrentUser();
	$data = $db->prepare( 'UPDATE users SET password = (:password) WHERE user = (:user);' );
	$data->bindParam( ':password', $password, PDO::PARAM_STR );
	$data->bindParam( ':user', $current_user, PDO::PARAM_STR );
	$data->execute();
	$html .= '<pre>Password Changed.</pre>';
}
?>
