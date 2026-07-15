<?php

require_once __DIR__ . "/redirect_targets.php";

$target = approved_redirect_target($_GET['redirect'] ?? null);
if ($target !== null) {
	header ("location: " . $target);
	exit;
}

http_response_code (400);
?>
<p>Unknown or missing redirect target.</p>
<?php
exit;
?>
