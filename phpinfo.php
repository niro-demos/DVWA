<?php

define( 'DVWA_WEB_PAGE_TO_ROOT', '' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated') );

// phpinfo() exposes database credentials, server paths and PHP version —
// restrict it to administrators only.
if( dvwaCurrentUser() != 'admin' ) {
	http_response_code( 403 );
	exit;
}

phpinfo();

?>
