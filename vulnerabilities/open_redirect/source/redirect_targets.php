<?php

function approved_redirect_target($requested_target) {
	$targets = array(
		"info.php?id=1" => "info.php?id=1",
		"info.php?id=2" => "info.php?id=2",
	);

	if (!is_string($requested_target) || !array_key_exists($requested_target, $targets)) {
		return null;
	}

	return $targets[$requested_target];
}

