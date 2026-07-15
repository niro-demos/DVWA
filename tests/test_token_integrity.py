import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_php(source: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["php"], input="<?php\n" + source, text=True, capture_output=True, cwd=ROOT, env={**os.environ, **(env or {})})

def test_high_tokens_reject_ciphertext_or_iv_tampering():
    result = run_php(r'''require 'vulnerabilities/cryptography/source/token_library_high.php';
$issued = json_decode(create_token(), true); $valid = json_decode(check_token(json_encode($issued)), true);
if (($valid['status'] ?? null) !== 200) { fwrite(STDERR, "valid token rejected\n"); exit(2); }
$iv = base64_decode($issued['iv'], true); $iv[7] = chr(ord($iv[7]) ^ 3); $issued['iv'] = base64_encode($iv);
$altered = json_decode(check_token(json_encode($issued)), true);
if (($altered['status'] ?? null) === 200) { fwrite(STDERR, "altered token accepted\n"); exit(1); }''')
    assert result.returncode == 0, result.stderr

def test_medium_rejects_recombined_ecb_token():
    result = run_php(r'''$_SERVER['REQUEST_METHOD'] = 'POST'; $_SERVER['PHP_SELF'] = '/vulnerabilities/cryptography/';
$_POST['token'] = '3061837c4f9debaf19d4539bfa0074c1174d4b2659239bbc50646e14a70becef837d1e6b16bfae07b776feb7afe57630caeb574f10f349ed839fbfd223903368873580b2e3e494ace1e9e8035f0e7e07';
require 'vulnerabilities/cryptography/source/medium.php';
if (str_contains($html, 'Welcome administrator Sweep')) { fwrite(STDERR, "recombined token accepted\n"); exit(1); }''')
    assert result.returncode == 0, result.stderr

def test_low_handler_exposes_no_credential_or_encryption_oracle():
    result = run_php(r'''$_SERVER['REQUEST_METHOD'] = 'POST'; $_SERVER['PHP_SELF'] = '/vulnerabilities/cryptography/';
$_POST = ['message' => 'AAAAAAAAAA', 'direction' => 'encode']; require 'vulnerabilities/cryptography/source/low.php';
if (str_contains($html, 'NiAiKTU2Li4zJQ==') || str_contains($html, 'Lg4WGlQZChhSFBYSEB8bBQtPGxdNQSwEHREOAQY=')) { fwrite(STDERR, "reusable-key credential oracle exposed\n"); exit(1); }''')
    assert result.returncode == 0, result.stderr

def test_api_rejects_token_forged_with_published_key():
    forged = "nOMAfAqXAMRKH86RqI2c2Do6Ojo6kv6Cafpzx37eCWzBOjo6Ojp4c3VxYWVoMm5ENENSVGNDbkpvc0Z1eEZGOHhkWnQyM1VUZ1JQQUkvRHJqbGIzUzMxLzQy"
    result = run_php(rf'''require 'vulnerabilities/api/src/Token.php'; require 'vulnerabilities/api/src/Login.php';
if (Src\Login::check_access_token('{forged}')) {{ fwrite(STDERR, "forged API token accepted\n"); exit(1); }}''')
    assert result.returncode == 0, result.stderr

def test_api_accepts_a_server_issued_token_with_deployment_secrets():
    result = run_php(r'''require 'vulnerabilities/api/src/Token.php'; require 'vulnerabilities/api/src/Login.php';
$tokens = json_decode(Src\Login::create_token(), true); if (!Src\Login::check_access_token($tokens['access_token'])) { fwrite(STDERR, "server-issued API token rejected\n"); exit(1); }''', {
        "DVWA_API_TOKEN_ENCRYPTION_KEY": "test-encryption-key-at-least-32-bytes", "DVWA_API_ACCESS_TOKEN_SECRET": "test-access-secret-at-least-32-bytes", "DVWA_API_REFRESH_TOKEN_SECRET": "test-refresh-secret-at-least-32-bytes"})
    assert result.returncode == 0, result.stderr
