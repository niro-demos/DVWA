<?php

// The page we wish to display. File inclusion is an application-resource
// selector, not a filesystem API: accept only the documented local pages.
$file = $_GET[ 'page' ];
$configFileNames = [
	'include.php',
	'file1.php',
	'file2.php',
	'file3.php',
];

if( !in_array( $file, $configFileNames, true ) ) {
	echo 'ERROR: File not found!';
	exit;
}

?>
