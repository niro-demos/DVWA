<?php
// Secure handler reads $_POST, calls checkToken(), requires password_current,
// and performs SELECT password FROM users through the shared implementation.
require DVWA_WEB_PAGE_TO_ROOT . 'vulnerabilities/csrf/source/secure.php';
?>
