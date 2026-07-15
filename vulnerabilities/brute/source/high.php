<?php

if( isset( $_POST[ 'Login' ] ) && isset( $_POST[ 'password' ] ) ) {
	checkToken( $_POST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' );
	$row = dvwaPasswordChallenge( $_POST[ 'password' ] );
	if( $row ) {
		$user = htmlspecialchars( dvwaCurrentUser(), ENT_QUOTES, 'UTF-8' );
		$avatar = htmlspecialchars( $row[ 'avatar' ], ENT_QUOTES, 'UTF-8' );
		$html .= "<p>Welcome to the password protected area {$user}</p>";
		$html .= "<img src=\"{$avatar}\" />";
	} else {
		sleep( rand( 0, 3 ) );
		$html .= "<pre><br />Username and/or password incorrect.</pre>";
	}
}

generateSessionToken();

?>
