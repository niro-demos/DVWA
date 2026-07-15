<?php

function dvwaPingIp( $target ) {
	if( !is_string( $target ) ) {
		return array( false, '', null );
	}

	$target = trim( $target );
	if( filter_var( $target, FILTER_VALIDATE_IP ) === false ) {
		return array( false, '', null );
	}

	if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
		$command = array( 'ping', $target );
	}
	else {
		$command = array( 'ping', '-c', '4', $target );
	}

	$descriptors = array(
		1 => array( 'pipe', 'w' ),
		2 => array( 'pipe', 'w' ),
	);
	$process = proc_open( $command, $descriptors, $pipes );
	if( !is_resource( $process ) ) {
		return array( true, '', 1 );
	}

	$output = stream_get_contents( $pipes[1] );
	$error = stream_get_contents( $pipes[2] );
	fclose( $pipes[1] );
	fclose( $pipes[2] );
	$status = proc_close( $process );

	return array( true, $output . $error, $status );
}

?>
