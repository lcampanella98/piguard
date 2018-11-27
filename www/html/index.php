<?php

function human_filesize($bytes, $decimals = 2) {
    $size = array('B','kB','MB','GB','TB','PB','EB','ZB','YB');
    $factor = floor((strlen($bytes) - 1) / 3);
    return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . @$size[$factor];
}
?>
<html>
	<head>
	<title>PiGuard</title>
	<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
	<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
	</head>

<body>
<div class="container">
	<h4 style="margin-top:10px;">PiGuard Surveillence System</h4><hr />
	
	<div style="text-align:center;">
		<img id="streamimage" src="<?php echo 'http://' . $_SERVER['SERVER_NAME'] . ":8080/?action=stream" ?>" />
		
		<?php
			$status_file_path = "piguard_stats.txt";
			$status_file = fopen($status_file_path, 'r') or NULL;
			if ($status_file) {
				$status_str = fread($status_file,filesize($status_file_path));
				$arr = explode("\t", $status_str);
				$total_bytes = $arr[0];
				$recorded_bytes = $arr[1];
				echo '<br /><table class="table table-bordered" style="margin-top: 15px;"><tbody>';
				echo "
				<tr>
					<td>Total information processed</td>
					<td>" . human_filesize($total_bytes) . "</td>
				</tr>
				<tr>
					<td>Total recorded motion</td>
					<td>" . human_filesize($recorded_bytes) . "</td>
				</tr>
				<tr>
					<td>Total space savings</td>
					<td>" . human_filesize($total_bytes - $recorded_bytes) . " (" . round(($total_bytes-$recorded_bytes)/$total_bytes*100,2) . "%)</td>";
				echo '</tbody></table>';
			}

		?>
	</div>
	<br />
	<a href="view_detected.php"><button type="button" class="btn btn-primary">View Detected</button></a>

	<div style="margin-top: 100px;"></div>
</div>
</body>
</html>
