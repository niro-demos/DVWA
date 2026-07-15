<?php

require dirname(__DIR__, 2) . '/vulnerabilities/api/src/HealthController.php';

$controller = new Src\HealthController($_SERVER['REQUEST_METHOD'], 2, 'connectivity');
$controller->processRequest();

