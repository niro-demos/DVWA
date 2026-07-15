<?php

namespace Src;

use OpenApi\Attributes as OAT;

class Login
{
	private const ACCESS_TOKEN_LIFE = 180;
	private const REFRESH_TOKEN_LIFE = 240;
	private const SECRET_FILE = '/tmp/dvwa-api-token-secrets.json';

	private static function secrets() {
		if (!file_exists(self::SECRET_FILE)) {
			self::rotateSecrets();
		}
		$data = json_decode((string) file_get_contents(self::SECRET_FILE), true);
		if (!is_array($data) || empty($data['access']) || empty($data['refresh'])) {
			throw new \RuntimeException('Token signing keys are unavailable');
		}
		return $data;
	}

	public static function rotateSecrets() {
		$data = json_encode(array(
			'access' => bin2hex(random_bytes(32)),
			'refresh' => bin2hex(random_bytes(32)),
		));
		$tmp = self::SECRET_FILE . '.' . bin2hex(random_bytes(6));
		if (file_put_contents($tmp, $data, LOCK_EX) === false || !rename($tmp, self::SECRET_FILE)) {
			@unlink($tmp);
			throw new \RuntimeException('Unable to rotate token signing keys');
		}
	}
	
	public static function create_token() {
		$now = time();
		$tokenObj = new Token();
		$secrets = self::secrets();
		$token = json_encode (array (
			"access_token" => $tokenObj->create_token($secrets['access'], $now + self::ACCESS_TOKEN_LIFE),
			"refresh_token" => $tokenObj->create_token($secrets['refresh'], $now + self::REFRESH_TOKEN_LIFE),
			"token_type" => "bearer",
			"expires_in" => self::ACCESS_TOKEN_LIFE)
		);
		return $token;
	}

	public static function check_access_token($token) {
		$tokenObj = new Token();
		$decrypted = $tokenObj->decrypt_token ($token);

		if ($decrypted === false) {
			return false;
		}
		if (isset($decrypted['secret'], $decrypted['expires']) && hash_equals(self::secrets()['access'], (string) $decrypted['secret']) && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}

	public static function check_refresh_token($token) {
		$tokenObj = new Token();
		$decrypted = $tokenObj->decrypt_token ($token);

		if ($decrypted !== false && isset($decrypted['secret'], $decrypted['expires']) && hash_equals(self::secrets()['refresh'], (string) $decrypted['secret']) && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}
}
