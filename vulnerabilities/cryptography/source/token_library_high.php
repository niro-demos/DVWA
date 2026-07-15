<?php

require_once __DIR__ . '/cryptography_key.php';

define('ALGO', 'aes-256-gcm');

function encrypt($plaintext, $iv) {
	if (strlen($iv) != 12) {
		throw new Exception('IV must be 12 bytes, ' . strlen($iv) . ' passed');
	}
	$ciphertext = openssl_encrypt($plaintext, ALGO, dvwa_cryptography_key(), OPENSSL_RAW_DATA, $iv, $tag);
	if ($ciphertext === false) {
		throw new Exception('Encryption failed');
	}
	return $ciphertext . $tag;
}

function decrypt($packed, $iv) {
	if (strlen($iv) != 12 || strlen($packed) < 17) {
		throw new Exception('Token is in wrong format');
	}
	$tag = substr($packed, -16);
	$ciphertext = substr($packed, 0, -16);
	$plaintext = openssl_decrypt($ciphertext, ALGO, dvwa_cryptography_key(), OPENSSL_RAW_DATA, $iv, $tag);
	if ($plaintext === false) {
		throw new Exception('Token authentication failed');
	}
	return $plaintext;
}

function create_token($debug = false) {
	$iv = random_bytes(12);
	return json_encode(array('token' => base64_encode(encrypt('userid:2', $iv)), 'iv' => base64_encode($iv)));
}

function check_token($data) {
	$users = array(
		1 => array('name' => 'Geoffery', 'level' => 'admin'),
		2 => array('name' => 'Bungle', 'level' => 'user'),
		3 => array('name' => 'Zippy', 'level' => 'user'),
		4 => array('name' => 'George', 'level' => 'user'),
	);
	$data_array = json_decode($data, true);
	if (!is_array($data_array)) {
		return json_encode(array('status' => 522, 'message' => 'Data in wrong format'));
	}
	if (!isset($data_array['token'], $data_array['iv'])) {
		return json_encode(array('status' => 523, 'message' => 'Missing token data'));
	}
	$ciphertext = base64_decode($data_array['token'], true);
	$iv = base64_decode($data_array['iv'], true);
	if ($ciphertext === false || $iv === false) {
		return json_encode(array('status' => 526, 'message' => 'Unable to decrypt token'));
	}
	try {
		$plaintext = decrypt($ciphertext, $iv);
	} catch (Exception $exception) {
		return json_encode(array('status' => 526, 'message' => 'Unable to decrypt token'));
	}
	if (!preg_match('/^userid:(\d+)$/', $plaintext, $matches) || !isset($users[$matches[1]])) {
		return json_encode(array('status' => 527, 'message' => 'No valid user specified'));
	}
	$user = $users[$matches[1]];
	return json_encode(array('status' => 200, 'user' => $user['name'], 'level' => $user['level']));
}

?>
