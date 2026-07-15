from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text()


class BacUserManagerSecurityTests(unittest.TestCase):
 def test_user_manager_routes_require_authenticated_admin(self):
    for endpoint in (
        "vulnerabilities/authbypass/get_user_data.php",
        "vulnerabilities/authbypass/change_user_details.php",
    ):
        php = source(endpoint)
        self.assertIn("dvwaPageStartup( array( 'authenticated' ) );", php)
        self.assertIn("dvwaCurrentUser() !== 'admin'", php)
        self.assertIn("http_response_code( 403 );", php)


 def test_user_manager_update_binds_all_submitted_values(self):
    php = source("vulnerabilities/authbypass/change_user_details.php")
    self.assertIn("FILTER_VALIDATE_INT", php)
    self.assertIn("UPDATE users SET first_name = ?, last_name = ? WHERE user_id = ?", php)
    self.assertIn("mysqli_stmt_bind_param", php)
    self.assertNotIn("SET first_name = '", php)


 def test_user_manager_builds_name_inputs_without_html_interpolation(self):
    javascript = source("vulnerabilities/authbypass/authbypass.js")
    self.assertIn(".value = user['first_name']", javascript)
    self.assertIn(".value = user['surname']", javascript)
    self.assertNotIn("value=\"' + user['first_name']", javascript)
    self.assertNotIn("value=\"' + user['surname']", javascript)


 def test_low_and_medium_profiles_use_server_identity_and_encode_names(self):
    for level in ("low", "medium"):
        php = source(f"vulnerabilities/bac/source/{level}.php")
        self.assertIn("$id === $current_user_id", php)
        self.assertIn("htmlspecialchars($row['first_name'], ENT_QUOTES, 'UTF-8')", php)
        self.assertIn("htmlspecialchars($row['last_name'], ENT_QUOTES, 'UTF-8')", php)

    low = source("vulnerabilities/bac/source/low.php")
    medium = source("vulnerabilities/bac/source/medium.php")
    self.assertNotIn("$_COOKIE['user_id']", low)
    self.assertNotIn("$_GET['token'] == 'user_token'", medium)


 def test_existing_secure_profile_renderer_is_a_positive_control(self):
    php = source("vulnerabilities/bac/source/impossible.php")
    self.assertIn("htmlspecialchars($row['first_name'], ENT_QUOTES, 'UTF-8')", php)
    self.assertIn("htmlspecialchars($row['last_name'], ENT_QUOTES, 'UTF-8')", php)


if __name__ == "__main__":
    unittest.main()
