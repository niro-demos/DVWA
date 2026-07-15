<?php

require_once __DIR__ . '/cryptography_key.php';

function create_medium_token($claims) {
	$iv = random_bytes(12);
	$ciphertext = openssl_encrypt(
		json_encode($claims),
		'aes-256-gcm',
		dvwa_cryptography_key(),
		OPENSSL_RAW_DATA,
		$iv,
		$tag
	);
	if ($ciphertext === false) {
		throw new Exception('Encryption failed');
	}
	return bin2hex($iv . $tag . $ciphertext);
}

function decrypt_medium_token($token) {
	$packed = ctype_xdigit($token) && strlen($token) % 2 === 0 ? hex2bin($token) : false;
	if ($packed === false || strlen($packed) < 29) {
		throw new Exception('Token is in wrong format');
	}
	$iv = substr($packed, 0, 12);
	$tag = substr($packed, 12, 16);
	$ciphertext = substr($packed, 28);
	$plaintext = openssl_decrypt(
		$ciphertext,
		'aes-256-gcm',
		dvwa_cryptography_key(),
		OPENSSL_RAW_DATA,
		$iv,
		$tag
	);
	if ($plaintext === false) {
		throw new Exception('Token authentication failed');
	}
	return $plaintext;
}

$errors = '';
$success = '';
$messages = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	try {
		if (!array_key_exists('token', $_POST)) {
			throw new Exception('No token passed');
		}
		$user = json_decode(decrypt_medium_token($_POST['token']));
		if ($user === null) {
			throw new Exception('Could not decode JSON object.');
		}
		if ($user->user == 'sweep' && $user->ex > time() && $user->level == 'admin') {
			$success = 'Welcome administrator Sweep';
		} else {
			$messages = 'Login successful but not as the right user.';
		}
	} catch (Exception $e) {
		$errors = $e->getMessage();
	}
}

$samples = array(
	array('label' => 'Sooty (admin), session expired', 'claims' => array('user' => 'sooty', 'ex' => time() - 3600, 'level' => 'admin', 'bio' => "Izzy wizzy let's get busy")),
	array('label' => 'Sweep (user), session expired', 'claims' => array('user' => 'sweep', 'ex' => time() - 3600, 'level' => 'user', 'bio' => 'Squeeeeek')),
	array('label' => 'Soo (user), session valid', 'claims' => array('user' => 'soo', 'ex' => time() + 3600, 'level' => 'user', 'bio' => 'I won The Weakest Link')),
);

$html = '<p>You have managed to get hold of three authenticated session tokens:</p>';
foreach ($samples as $sample) {
	$html .= '<p><strong>' . htmlentities($sample['label']) . '</strong></p>';
	$html .= "<p><textarea style='width: 600px; height: 56px'>" . htmlentities(create_medium_token($sample['claims'])) . '</textarea></p>';
}
$html .= '<p>Authenticated encryption prevents a captured token from being altered or rearranged.</p><hr>';

if ($errors != '') {
	$html .= '<div class="warning">' . htmlentities($errors) . '</div>';
}
if ($messages != '') {
	$html .= '<div class="nearly">' . htmlentities($messages) . '</div>';
}
if ($success != '') {
	$html .= '<div class="success">' . htmlentities($success) . '</div>';
}

$html .= '<form name="token" method="post" action="' . htmlentities($_SERVER['PHP_SELF']) . '">
	<p><label for="token">Token:</label><br><textarea style="width: 600px; height: 56px" id="token" name="token"></textarea></p>
	<p><input type="submit" value="Submit"></p></form>';

?>
