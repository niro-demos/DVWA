<?php

require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaQuery.inc.php';

if (isset($_POST['Submit'])) {
	global $sqlite_db_connection;
	$id = $_POST['id'];
	$row = dvwaUserById($id, $_DVWA['SQLI_DB'], $db, $sqlite_db_connection);
	if ($row !== null) {
		$html .= "<pre>ID: {$id}<br />First name: {$row['first_name']}<br />Surname: {$row['last_name']}</pre>";
	}
}

$query = 'SELECT COUNT(*) FROM users;';
$result = mysqli_query($GLOBALS['___mysqli_ston'], $query) or die('<pre>Something went wrong.</pre>');
$number_of_rows = mysqli_fetch_row($result)[0];

?>
