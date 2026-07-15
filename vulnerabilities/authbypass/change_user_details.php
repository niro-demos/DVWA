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

if ($_SERVER['REQUEST_METHOD'] != "POST") {
	$result = array (
						"result" => "fail",
						"error" => "Only POST requests are accepted"
					);
	echo json_encode($result);
	exit;
}

try {
	$json = file_get_contents('php://input');
	$data = json_decode($json);
	if (is_null ($data)) {
		$result = array (
							"result" => "fail",
							"error" => 'Invalid format, expecting "{id: {user ID}, first_name: "{first name}", surname: "{surname}"}'

						);
		echo json_encode($result);
		exit;
	}
} catch (Exception $e) {
	$result = array (
						"result" => "fail",
						"error" => 'Invalid format, expecting \"{id: {user ID}, first_name: "{first name}", surname: "{surname}\"}'

					);
	echo json_encode($result);
	exit;
}

$id = filter_var( $data->id ?? null, FILTER_VALIDATE_INT );
if ( $id === false || !isset( $data->first_name, $data->surname ) || !is_string( $data->first_name ) || !is_string( $data->surname ) ) {
	http_response_code( 400 );
	print json_encode( array( 'result' => 'fail', 'error' => 'Invalid user details' ) );
	exit;
}

$stmt = mysqli_prepare(
	$GLOBALS['___mysqli_ston'],
	'UPDATE users SET first_name = ?, last_name = ? WHERE user_id = ?'
);
if ( !$stmt ) {
	http_response_code( 500 );
	print json_encode( array( 'result' => 'fail', 'error' => 'Database error' ) );
	exit;
}

mysqli_stmt_bind_param( $stmt, 'ssi', $data->first_name, $data->surname, $id );
if ( !mysqli_stmt_execute( $stmt ) ) {
	mysqli_stmt_close( $stmt );
	http_response_code( 500 );
	print json_encode( array( 'result' => 'fail', 'error' => 'Database error' ) );
	exit;
}
mysqli_stmt_close( $stmt );

print json_encode (array ("result" => "ok"));
exit;
?>
