<?php

namespace Src;

use OpenApi\Attributes as OAT;

class Login
{
	private const ACCESS_TOKEN_LIFE = 180;
	private const REFRESH_TOKEN_LIFE = 240;

	private static function secret($name) {
		$value = getenv($name);
		if ($value === false || strlen($value) < 32) {
			throw new \RuntimeException($name . ' must be at least 32 bytes');
		}
		return $value;
	}
	
	public static function create_token() {
		$now = time();
		$tokenObj = new Token();
		$token = json_encode (array (
			"access_token" => $tokenObj->create_token(self::secret('DVWA_API_ACCESS_TOKEN_SECRET'), $now + self::ACCESS_TOKEN_LIFE),
			"refresh_token" => $tokenObj->create_token(self::secret('DVWA_API_REFRESH_TOKEN_SECRET'), $now + self::REFRESH_TOKEN_LIFE),
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
		try { $secret = self::secret('DVWA_API_ACCESS_TOKEN_SECRET'); } catch (\RuntimeException $e) { return false; }
		if (isset($decrypted['secret'], $decrypted['expires']) && hash_equals($secret, $decrypted['secret']) && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}

	public static function check_refresh_token($token) {
		$tokenObj = new Token();
		$decrypted = $tokenObj->decrypt_token ($token);

		if ($decrypted === false) { return false; }
		try { $secret = self::secret('DVWA_API_REFRESH_TOKEN_SECRET'); } catch (\RuntimeException $e) { return false; }
		if (isset($decrypted['secret'], $decrypted['expires']) && hash_equals($secret, $decrypted['secret']) && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}
}
