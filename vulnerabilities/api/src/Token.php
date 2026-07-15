<?php

namespace Src;

use OpenApi\Attributes as OAT;

#[OAT\Schema(required: ['token'])]
class Token {
	private const ENCRYPTION_CIPHER = "aes-128-gcm";
	private static function encryption_key() {
		$key = getenv('DVWA_API_TOKEN_ENCRYPTION_KEY');
		if ($key === false || strlen($key) < 32) {
			throw new \RuntimeException('DVWA_API_TOKEN_ENCRYPTION_KEY must be at least 32 bytes');
		}
		return $key;
	}

    # Not sure if this is needed
    #[OAT\Property(example: "11111")]
	public string $token;

	private string $secret;
	private int $expires;

	public function __construct () {
	}

	private static function encrypt($cleartext) {
		$ivlen = openssl_cipher_iv_length(self::ENCRYPTION_CIPHER);
		$iv = openssl_random_pseudo_bytes($ivlen);
		$ciphertext = openssl_encrypt($cleartext, self::ENCRYPTION_CIPHER, self::encryption_key(), $options=0, $iv, $tag);
		$ret = base64_encode ($tag . ":::::" . $iv . ":::::" . $ciphertext);
		return $ret;
	}

	private static function decrypt($ciphertext) {
		$str = base64_decode ($ciphertext);
		$bits = explode (":::::", $str);
		if (count ($bits) != 3) {
			return false;
		}
		$value = $bits[2];
		$iv = $bits[1];
		$tag = $bits[0];
		try {
			$key = self::encryption_key();
		} catch (\RuntimeException $e) {
			return false;
		}
		$cleartext = openssl_decrypt($value, self::ENCRYPTION_CIPHER, $key, $options=0, $iv, $tag);
		return $cleartext;
	}
	public function create_token($secret, $expires) {
		$token = self::encrypt (json_encode (array (
						"secret" => $secret,
						"expires" => $expires,
					)));
		return $token;
	}

	public function decrypt_token($token) {
		$decrypted = self::decrypt($token);

		if ($decrypted === false) {
			return false;
		}

		$token = json_decode ($decrypted, true);
		return $token;
	}
}

?>
