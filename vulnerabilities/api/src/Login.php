<?php

namespace Src;

use OpenApi\Attributes as OAT;

class Login
{
	private const ACCESS_TOKEN_LIFE = 180;
	private const REFRESH_TOKEN_LIFE = 240;

	/**
	 * Load the access-token secret from the API_TOKEN_SECRET environment
	 * variable. There is NO hardcoded fallback — a missing secret causes all
	 * access-token validation to fail closed (reject every token).
	 */
	private static function getAccessTokenSecret(): string|false {
		$secret = getenv('API_TOKEN_SECRET');
		return ($secret === false || $secret === '') ? false : $secret;
	}

	/**
	 * Load the refresh-token secret from the API_REFRESH_TOKEN_SECRET
	 * environment variable. Same fail-closed policy as the access token.
	 */
	private static function getRefreshTokenSecret(): string|false {
		$secret = getenv('API_REFRESH_TOKEN_SECRET');
		return ($secret === false || $secret === '') ? false : $secret;
	}

	public static function create_token() {
		$now = time();
		$tokenObj = new Token();
		$accessSecret = self::getAccessTokenSecret();
		$refreshSecret = self::getRefreshTokenSecret();
		$token = json_encode (array (
			"access_token" => $accessSecret !== false ? $tokenObj->create_token($accessSecret, $now + self::ACCESS_TOKEN_LIFE) : false,
			"refresh_token" => $refreshSecret !== false ? $tokenObj->create_token($refreshSecret, $now + self::REFRESH_TOKEN_LIFE) : false,
			"token_type" => "bearer",
			"expires_in" => self::ACCESS_TOKEN_LIFE)
		);
		return $token;
	}

	public static function check_access_token($token) {
		$secret = self::getAccessTokenSecret();
		if ($secret === false) {
			return false;
		}
		$tokenObj = new Token();
		$decrypted = $tokenObj->decrypt_token ($token);

		if ($decrypted === false) {
			return false;
		}
		if ($decrypted['secret'] == $secret && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}

	public static function check_refresh_token($token) {
		$secret = self::getRefreshTokenSecret();
		if ($secret === false) {
			return false;
		}
		$tokenObj = new Token();
		$decrypted = $tokenObj->decrypt_token ($token);

		if ($decrypted === false) {
			return false;
		}
		if ($decrypted['secret'] == $secret && $decrypted['expires'] > time()) {
			return true;
		}
		return false;
	}
}
