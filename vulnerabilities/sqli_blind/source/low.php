<?php

require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaQuery.inc.php';

if (isset($_GET['Submit'])) {
	global $sqlite_db_connection;
	$id = $_GET['id'];
	$exists = dvwaUserById($id, $_DVWA['SQLI_DB'], $db, $sqlite_db_connection) !== null;
	if ($exists) {
		$html .= '<pre>User ID exists in the database.</pre>';
	} else {
		header($_SERVER['SERVER_PROTOCOL'] . ' 404 Not Found');
		$html .= '<pre>User ID is MISSING from the database.</pre>';
	}
}

?>
