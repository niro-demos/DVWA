<?php
define( 'DVWA_WEB_PAGE_TO_ROOT', '../../' );
require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup( array( 'authenticated' ) );

if ( dvwaCurrentUser() !== 'admin' ) {
	http_response_code( 403 );
	print json_encode( array( 'result' => 'fail', 'error' => 'Access denied' ) );
	exit;
}

dvwaDatabaseConnect();

$query  = "SELECT user_id, first_name, last_name FROM users";
$result = mysqli_query($GLOBALS["___mysqli_ston"],  $query );

$guestbook = ''; 
$users = array();

while ($row = mysqli_fetch_row($result) ) {
	$user_id = $row[0];
	$first_name = $row[1];
	$surname = $row[2];

	$user = array (
					"user_id" => $user_id,
					"first_name" => $first_name,
					"surname" => $surname
				);
	$users[] = $user;
}

print json_encode ($users);
exit;
?>
