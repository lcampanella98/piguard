<?php
$vids_dir = "./detected";


function human_filesize($bytes, $decimals = 2) {
    $size = array('B','kB','MB','GB','TB','PB','EB','ZB','YB');
    $factor = floor((strlen($bytes) - 1) / 3);
    return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . @$size[$factor];
}
?>

<?php
if (isset($_GET['del'])) {
	$del = urldecode($_GET['del']);
	unlink($vids_dir . '/' . $del);
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
	<h4 style="margin-top:10px;">Detected Motion</h4><hr />
	<?php
		$motion_vids = scandir($vids_dir, SCANDIR_SORT_DESCENDING);
		foreach ($motion_vids as $vid) {
			if ($vid === '.' || $vid === '..') continue;
			echo '<div class="row" style="margin-top: 10px;">';
			echo "<div class='col-sm-4'><a href=\"{$vids_dir}/{$vid}\">{$vid}</a><a href=\"{$vids_dir}/{$vid}\" download></div>";
			echo "<div class='col-sm-4'><button type=\"button\" class=\"btn btn-primary\">Download (" . human_filesize(filesize($vids_dir."/".$vid)) . ")</button></a></div>";
			echo "<div class='col-sm-4'><a href=\"./view_detected.php?del=" . urlencode($vid) . "\"><button type=\"button\" class=\"btn btn-danger\">Delete</button></a></div>";
			echo "</div>";

		}
	?>
	<a href="index.php"><button type="button" class="btn btn-default">Back</button></a>

	<div style="margin-bottom:100px;"></div>
</div>

</body>
</html>
