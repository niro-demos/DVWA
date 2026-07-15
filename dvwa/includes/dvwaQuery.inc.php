<?php

function dvwaValidatedUserId($value) {
	$id = filter_var($value, FILTER_VALIDATE_INT);
	return $id === false ? null : $id;
}

function dvwaUserById($value, $databaseType, $db, $sqliteDb) {
	$id = dvwaValidatedUserId($value);
	if ($id === null) {
		return null;
	}

	if ($databaseType === MYSQL) {
		$stmt = $db->prepare('SELECT first_name, last_name FROM users WHERE user_id = (:id) LIMIT 1;');
		$stmt->bindValue(':id', $id, PDO::PARAM_INT);
		$stmt->execute();
		$row = $stmt->fetch(PDO::FETCH_ASSOC);
		return $row === false ? null : $row;
	}

	$stmt = $sqliteDb->prepare('SELECT first_name, last_name FROM users WHERE user_id = :id LIMIT 1;');
	$stmt->bindValue(':id', $id, SQLITE3_INTEGER);
	$result = $stmt->execute();
	if ($result === false) {
		return null;
	}
	$row = $result->fetchArray(SQLITE3_ASSOC);
	$result->finalize();
	return $row === false ? null : $row;
}

?>
