<?php

if( isset( $_POST[ 'Upload' ] ) ) {
	$uploaded_name = $_FILES[ 'uploaded' ][ 'name' ];
	$uploaded_ext  = strtolower( pathinfo( $uploaded_name, PATHINFO_EXTENSION ) );
	$uploaded_size = $_FILES[ 'uploaded' ][ 'size' ];
	$uploaded_tmp  = $_FILES[ 'uploaded' ][ 'tmp_name' ];
	$image_info    = @getimagesize( $uploaded_tmp );

	$allowed_types = [ IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png' ];
	$image_type    = $image_info[2] ?? null;

	if( isset( $allowed_types[ $image_type ] ) &&
		in_array( $uploaded_ext, [ 'jpg', 'jpeg', 'png' ], true ) &&
		$uploaded_size < 100000 ) {

		$target_path = DVWA_WEB_PAGE_TO_ROOT . 'hackable/uploads/';
		$target_file = bin2hex( random_bytes( 16 ) ) . '.' . $allowed_types[ $image_type ];
		$temp_file   = tempnam( sys_get_temp_dir(), 'dvwa-upload-' );
		$img         = $image_type === IMAGETYPE_JPEG
			? @imagecreatefromjpeg( $uploaded_tmp )
			: @imagecreatefrompng( $uploaded_tmp );

		$encoded = false;
		if( $img !== false && $temp_file !== false ) {
			$encoded = $image_type === IMAGETYPE_JPEG
				? imagejpeg( $img, $temp_file, 100 )
				: imagepng( $img, $temp_file, 9 );
			imagedestroy( $img );
		}

		if( $encoded && rename( $temp_file, getcwd() . DIRECTORY_SEPARATOR . $target_path . $target_file ) ) {
			$html .= "<pre><a href='{$target_path}{$target_file}'>{$target_file}</a> succesfully uploaded!</pre>";
		}
		else {
			$html .= '<pre>Your image was not uploaded.</pre>';
		}

		if( $temp_file !== false && file_exists( $temp_file ) ) {
			unlink( $temp_file );
		}
	}
	else {
		$html .= '<pre>Your image was not uploaded. We can only accept JPEG or PNG images.</pre>';
	}
}

?>
