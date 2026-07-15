from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source(path):
	return (ROOT / path).read_text()


def test_credential_checker_encodes_usernames_and_limits_guesses():
	code = source("vulnerabilities/csrf/test_credentials.php")
	assert "htmlspecialchars" in code
	assert "credential_attempts" in code
	assert "http_response_code( 429 )" in code


def test_csrf_password_changes_are_post_only_and_token_bound():
	page = source("vulnerabilities/csrf/index.php")
	assert 'method=\\"POST\\"' in page
	for level in ("low", "medium", "high", "impossible"):
		code = source(f"vulnerabilities/csrf/source/{level}.php")
		assert "$_POST" in code
		assert "$_GET" not in code
		assert "$_REQUEST" not in code
		assert "checkToken(" in code


def test_csrf_password_change_requires_current_password_at_every_level():
	page = source("vulnerabilities/csrf/index.php")
	assert "password_current" in page
	for level in ("low", "medium", "high", "impossible"):
		code = source(f"vulnerabilities/csrf/source/{level}.php")
		assert "password_current" in code
		assert "SELECT password FROM users" in code


def test_captcha_steps_use_server_side_one_time_state():
	for level in ("low", "medium"):
		code = source(f"vulnerabilities/captcha/source/{level}.php")
		assert "captcha_change" in code
		assert "random_bytes" in code
		assert "hash_equals" in code
		assert "passed_captcha" not in code


def test_high_captcha_requires_current_password_and_real_verification():
	page = source("vulnerabilities/captcha/index.php")
	code = source("vulnerabilities/captcha/source/high.php")
	assert "password_current" in page
	assert "password_current" in code
	assert "SELECT password FROM users" in code
	assert "hidd3n_valu3" not in code
	assert "HTTP_USER_AGENT" not in code
