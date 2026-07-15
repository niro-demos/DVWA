<?php

require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/command.php';

if( isset( $_POST[ 'Submit' ]  ) ) {
	// Get input
	$target = $_REQUEST[ 'ip' ];

	list( $valid, $cmd ) = dvwaPingIp( $target );
	if( !$valid ) {
		$html .= '<pre>Invalid IP address</pre>';
		return;
	}

	// Feedback for the end user
	$html .= "<pre>{$cmd}</pre>";
}

?>
