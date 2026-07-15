<?php

require_once DVWA_WEB_PAGE_TO_ROOT . 'dvwa/includes/dvwaQuery.inc.php';

if (isset($_REQUEST['Submit'])) {
	global $sqlite_db_connection;
	$id = $_REQUEST['id'];
	$row = dvwaUserById($id, $_DVWA['SQLI_DB'], $db, $sqlite_db_connection);
	if ($row !== null) {
		$html .= "<pre>ID: {$id}<br />First name: {$row['first_name']}<br />Surname: {$row['last_name']}</pre>";
	}
}

?>
