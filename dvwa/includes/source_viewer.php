<?php

/**
 * Resolve a source-viewer selection without allowing request data into a path.
 */
function dvwaSourceFile(string $id, string $security, string $extension = 'php'): ?string
{
	$ids = [
		'authbypass', 'bac', 'brute', 'csrf', 'exec', 'fi', 'javascript',
		'open_redirect', 'sqli', 'sqli_blind', 'upload', 'weak_id', 'xss_r', 'xss_s',
	];
	$levels = ['low', 'medium', 'high', 'impossible'];
	$extensions = ['php', 'js'];

	if (!in_array($id, $ids, true) || !in_array($security, $levels, true) || !in_array($extension, $extensions, true)) {
		return null;
	}

	$path = dirname(__DIR__, 2) . "/vulnerabilities/{$id}/source/{$security}.{$extension}";
	return is_file($path) ? $path : null;
}
