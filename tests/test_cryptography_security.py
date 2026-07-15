import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_php(program):
    result = subprocess.run(
        ["php", "-r", program],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result.stdout


def test_low_security_decoder_does_not_reveal_a_reusable_password():
    source = ROOT / "vulnerabilities/cryptography/source/low.php"
    control = run_php(f'''
        $_SERVER["REQUEST_METHOD"] = "POST";
        $_SERVER["PHP_SELF"] = "/vulnerabilities/cryptography/";
        $_POST = ["password" => "definitely-wrong"];
        require {json.dumps(str(source))};
        echo $html;
    ''')
    assert "Login Failed" in control
    assert "Welcome back user" not in control

    program = f'''
        $_SERVER["REQUEST_METHOD"] = "POST";
        $_SERVER["PHP_SELF"] = "/vulnerabilities/cryptography/";
        $_POST = ["direction" => "decode", "message" => "Lg4WGlQZChhSFBYSEB8bBQtPGxdNQSwEHREOAQY="];
        require {json.dumps(str(source))};
        echo $html;
    '''
    output = run_php(program)
    assert "Enter the account password" in output
    assert "Your new password is: Olifant" not in output
    assert ">Olifant<" not in output


def test_medium_tokens_reject_caller_minted_admin_claims():
    source = ROOT / "vulnerabilities/cryptography/source/medium.php"
    program = f'''
        $_SERVER["REQUEST_METHOD"] = "POST";
        $_SERVER["PHP_SELF"] = "/vulnerabilities/cryptography/";
        $claims = json_encode(["user" => "sweep", "ex" => time() + 3600, "level" => "admin", "bio" => "test"]);
        $_POST = ["token" => bin2hex(openssl_encrypt($claims, "aes-128-ecb", "ik ben een aardbei", OPENSSL_RAW_DATA))];
        require {json.dumps(str(source))};
        echo $html;
    '''
    output = run_php(program)
    assert 'name="token"' in output
    assert "Welcome administrator Sweep" not in output


def test_medium_tokens_reject_rearranged_ciphertext_blocks():
    source = ROOT / "vulnerabilities/cryptography/source/medium.php"
    program = f'''
        $_SERVER["REQUEST_METHOD"] = "POST";
        $_SERVER["PHP_SELF"] = "/vulnerabilities/cryptography/";
        $_POST = ["token" => "3061837c4f9debaf19d4539bfa0074c1174d4b2659239bbc50646e14a70becef837d1e6b16bfae07b776feb7afe576305aec34b41499579d3fb6acc8dc92fd5fcea8743c3b2904de83944d6b19733cdb48dd16048ed89967c250ab7f00629dba"];
        require {json.dumps(str(source))};
        echo $html;
    '''
    output = run_php(program)
    assert 'name="token"' in output
    assert "Welcome administrator Sweep" not in output


def test_high_security_tokens_detect_iv_tampering():
    library = ROOT / "vulnerabilities/cryptography/source/token_library_high.php"
    program = f'''
        require {json.dumps(str(library))};
        $legitimate = json_decode(create_token(), true);
        $legitimate_result = json_decode(check_token(json_encode($legitimate)), true);
        if (($legitimate_result["status"] ?? null) !== 200 || ($legitimate_result["level"] ?? null) !== "user") {{
            fwrite(STDERR, "legitimate token was rejected"); exit(1);
        }}
        $iv = base64_decode($legitimate["iv"], true);
        $iv[7] = $iv[7] ^ chr(3);
        $legitimate["iv"] = base64_encode($iv);
        echo check_token(json_encode($legitimate));
    '''
    result = json.loads(run_php(program))
    assert result["status"] != 200


def test_ecb_attack_helper_is_not_downloadable():
    download = ROOT / "vulnerabilities/cryptography/source/download_ecb_attack.php"
    helper = ROOT / "vulnerabilities/cryptography/source/ecb_attack.php"
    help_text = (ROOT / "vulnerabilities/cryptography/help/help.php").read_text()
    assert not download.exists()
    assert not helper.exists()
    assert "ik ben een aardbei" not in help_text
    assert "Olifant" not in help_text
