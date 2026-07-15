<?php

require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaQuery.inc.php';

if (isset($_POST['Submit'])) {
	global $sqlite_db_connection;
	$id = $_POST['id'];
	$exists = dvwaUserById($id, $_DVWA['SQLI_DB'], $db, $sqlite_db_connection) !== null;
	$html .= $exists
		? '<pre>User ID exists in the database.</pre>'
		: '<pre>User ID is MISSING from the database.</pre>';
}

?>
