<?php

function dvwa_cryptography_key() {
	$configured = getenv('DVWA_CRYPTOGRAPHY_KEY');
	if ($configured !== false && strlen($configured) >= 32) {
		return hash('sha256', $configured, true);
	}

	$key_file = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'dvwa-cryptography.key';
	$handle = fopen($key_file, 'c+b');
	if ($handle === false || !flock($handle, LOCK_EX)) {
		throw new Exception('Unable to initialize the cryptography key');
	}

	$key = stream_get_contents($handle);
	if (strlen($key) !== 32) {
		$key = random_bytes(32);
		ftruncate($handle, 0);
		rewind($handle);
		if (fwrite($handle, $key) !== 32 || !fflush($handle)) {
			flock($handle, LOCK_UN);
			fclose($handle);
			throw new Exception('Unable to persist the cryptography key');
		}
		chmod($key_file, 0600);
	}

	flock($handle, LOCK_UN);
	fclose($handle);
	return $key;
}

?>
